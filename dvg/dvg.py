from typing import Iterable, Iterator, List, Optional

from glob import iglob
import importlib
import io
from multiprocessing import Pool
from multiprocessing.shared_memory import SharedMemory
import os
import platform
import sys
from time import time

from docopt import docopt
from init_attrs_with_kwargs import InitAttrsWKwArgs
import numpy as np

from .iter_funcs import chunked_iter, sliding_window_iter
from .models import SCDVModel, find_model_specs
from .scanners import Scanner, ScanError
from .search_result import ANSI_ESCAPE_CLEAR_CUR_LINE, SLPPD, excerpt_text, trim_search_results, print_intermediate_search_result, prune_overlapped_paragraphs
from .text_funcs import includes_all_texts, includes_any_of_texts


_script_dir = os.path.dirname(os.path.realpath(__file__))


def model_shared(model: SCDVModel):
    shms = []

    model.tokenizer = None

    emb = model.embedder

    cvs = emb.cluster_idf_wvs
    shmc = SharedMemory(create=True, size=cvs.nbytes)
    shms.append(shmc)
    cvs_shared = np.ndarray(cvs.shape, dtype=cvs.dtype, buffer=shmc.buf)
    cvs_shared[:] = cvs[:]
    emb.cluster_idf_wvs = cvs_shared

    return shms


def model_shared_close(shms):
    for shm in shms:
        shm.close()
        shm.unlink()


VERSION = importlib.metadata.version("dvg")
DEFAULT_TOP_N = 20
DEFAULT_WINDOW_SIZE = 20
DEFAULT_EXCERPT_CHARS = 80
DEFAULT_PREFER_LONGER_THAN = 80


class CLArgs(InitAttrsWKwArgs):
    query: str
    file: List[str]
    verbose: bool
    model: str
    top_n: int
    paragraph_search: bool
    window: int
    include: List[str]
    exclude: List[str]
    min_length: int
    excerpt_length: int
    header: bool
    workers: Optional[int]
    help: bool
    version: bool
    over_pruning: float


__doc__: str = """Document-vector Grep.

Usage:
  dvg [options] [-i TEXT]... [-e TEXT]... -m MODEL <query> <file>...
  dvg --help
  dvg --version

Options:
  --verbose, -v                 Verbose.
  --model=MODEL, -m MODEL       Model name.
  --top-n=NUM, -n NUM           Show top NUM files [default: {dtn}].
  --paragraph-search, -p        Search paragraphs in documents.
  --window=NUM, -w NUM          Line window size [default: {dws}].
  --include=TEXT, -i TEXT       Requires containing the specified text.
  --exclude=TEXT, -e TEXT       Requires not containing the specified text.
  --min-length=CHARS, -l CHARS  Paragraphs shorter than this get a penalty [default: {dplt}].
  --excerpt-length=CHARS, -t CHARS      Length of the text to be excerpted [default: {dec}].
  --header, -H                  Print the header line.
  --workers=WORKERS -j WORKERS  Worker process.
  --over-pruning=RATIO, -P RATIO        No effect (only for compatibility to dvgi).
""".format(
    dtn=DEFAULT_TOP_N, dws=DEFAULT_WINDOW_SIZE, dplt=DEFAULT_PREFER_LONGER_THAN, dec=DEFAULT_EXCERPT_CHARS
)


def expand_file_iter(target_files: Iterable[str]) -> Iterator[str]:
    for f in target_files:
        if f == "-":
            for L in sys.stdin:
                L = L.rstrip()
                yield L
        elif "*" in f:
            for gf in iglob(f, recursive=True):
                if os.path.isfile(gf):
                    yield gf
        else:
            yield f


def find_similar_paragraphs(doc_files: Iterable[str], model: SCDVModel, a: CLArgs) -> List[SLPPD]:
    scanner = Scanner()

    search_results: List[SLPPD] = []
    sim_min_req = 0.5
    for df in doc_files:
        # read lines from document file
        try:
            lines = scanner.scan(df)
        except ScanError as e:
            print("> Warning: %s" % e, file=sys.stderr)
            continue

        # for each paragraph in the file, calculate the similarity to the query
        slppds: List[SLPPD] = []
        for pos in sliding_window_iter(len(lines), a.window):
            para = lines[pos[0] : pos[1]]
            para_len = sum(len(L) for L in para)
            if a.include and not includes_all_texts(para, a.include) or a.exclude and includes_any_of_texts(para, a.exclude):
                continue  # for pos, para

            sim = model.similarity_to_lines(para)
            if sim < sim_min_req:
                continue  # for pos, para

            if para_len < a.min_length:  # penalty for short paragraphs
                sim = sim * para_len / a.min_length
                if sim < sim_min_req:
                    continue  # for pos, para

            slppds.append((sim, para_len, pos, lines, df))

        if not slppds:
            continue  # for df

        # pick up paragraphs for the file
        if a.paragraph_search:
            slppds = prune_overlapped_paragraphs(slppds)  # remove paragraphs that overlap
            slppds.sort(reverse=True)
            del slppds[a.top_n :]
        else:
            slppds = [max(slppds)]  # extract only the most similar paragraphs in the file

        # update search results
        search_results.extend(slppds)
        if len(search_results) >= a.top_n * (2 if sim_min_req > 0.5 else 1):
            trim_search_results(search_results, a.top_n)
            sim_min_req = search_results[-1][0]

    trim_search_results(search_results, a.top_n)
    return search_results


def find_similar_paragraphs_i(arg_tuple):
    # (dfs, model, a) = arg_tuple
    r = find_similar_paragraphs(*arg_tuple)
    return r, arg_tuple[0]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=sys.stdout.encoding, errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=sys.stderr.encoding, errors="replace")

    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--bin-dir":
            print(os.path.join(_script_dir, "bin"))
            return
        if a == "--model-dir":
            print(os.path.join(_script_dir, "models"))
            return

    # A charm to make ANSI escape sequences work on Windows
    if platform.system() == "Windows":
        import colorama

        colorama.init()

    # command-line analysis
    argv = sys.argv[1:]
    raw_args = docopt(__doc__, argv=argv, version="dvg %s" % VERSION)
    a = CLArgs(_cast_str_values=True, **raw_args)

    # 1. model
    s = find_model_specs(a.model)
    if s is None:
        sys.exit("Error: model not found: %s" % a.model)
    tokenizer, model_file = s.tokenizer_name, s.model_file_path
    model = SCDVModel(tokenizer, model_file)

    # 2. query
    query_lines = [a.query]
    model.set_query(query_lines)

    count_document_files = 0
    chunk_size = 10000
    shms = None
    try:
        # search for document files that are similar to the query
        if a.verbose:
            print("", end="", file=sys.stderr)
        search_results: List[SLPPD] = []
        t0 = time()
        try:
            if a.workers and a.workers >= 2:
                shms = model_shared(model)  # load the model into shared memory for process parallel
                args_it = ((dfs, model, a) for dfs in chunked_iter(expand_file_iter(a.file), chunk_size))
                with Pool(processes=a.workers) as pool:
                    for srs, dfs in pool.imap_unordered(find_similar_paragraphs_i, args_it):
                        search_results.extend(srs)
                        trim_search_results(search_results, a.top_n)
                        count_document_files += len(dfs)
                        if a.verbose:
                            print_intermediate_search_result(search_results, count_document_files, time() - t0)
            else:
                for dfs in chunked_iter(expand_file_iter(a.file), chunk_size):
                    search_results.extend(find_similar_paragraphs(dfs, model, a))
                    trim_search_results(search_results, a.top_n)
                    count_document_files += len(dfs)
                    if a.verbose:
                        print_intermediate_search_result(search_results, count_document_files, time() - t0)
        except FileNotFoundError as e:
            if a.verbose:
                print(ANSI_ESCAPE_CLEAR_CUR_LINE, file=sys.stderr)
            sys.exit(str(e))
        except KeyboardInterrupt:
            if a.verbose:
                print(ANSI_ESCAPE_CLEAR_CUR_LINE + "> Interrupted. Shows the search results up to now.\n" + "> number of document files: %d" % count_document_files, file=sys.stderr)
        else:
            if a.verbose:
                print(ANSI_ESCAPE_CLEAR_CUR_LINE + "> number of document files: %d" % count_document_files, file=sys.stderr)

        # output search results
        trim_search_results(search_results, a.top_n)
        if a.header:
            print("\t".join(["sim", "chars", "location", "text"]))
        for sim, para_len, (b, e), lines, df in search_results:
            if sim < 0.5:
                break
            para = lines[b:e]
            excerpt = excerpt_text(para, model.similarity_to_lines, a.excerpt_length)
            print("%.4f\t%d\t%s:%d-%d\t%s" % (sim, para_len, df, b + 1, e, excerpt))
    finally:
        if shms is not None:
            model_shared_close(shms)


if __name__ == "__main__":
    main()
