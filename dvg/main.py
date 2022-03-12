from typing import Callable, Iterable, Iterator, List, Optional, Tuple

from glob import iglob
import importlib
from multiprocessing import Pool
from multiprocessing.shared_memory import SharedMemory
import os
import platform
import sys
from time import time

from docopt import docopt
from init_attrs_with_kwargs import InitAttrsWKwArgs
import numpy as np

from .iter_funcs import chunked_iter, ranges_overwrapping, sliding_window_iter
from .models import Model, SCDVModel, CombinedModel, Vec, inner_product_n, find_model_specs
from . import scanners
from .text_funcs import includes_all_texts, includes_any_of_texts


_script_dir = os.path.dirname(os.path.realpath(__file__))


def model_shared(model: Model):
    shms = []
    if isinstance(model, CombinedModel):
        for m in model.models:
            shms.extend(model_shared(m))
    elif isinstance(model, SCDVModel):
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
_ANSI_ESCAPE_CLEAR_CUR_LINE = "\x1b[1K\n\x1b[1A"


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


Pos = Tuple[int, int]
SPPD = Tuple[float, int, Pos, List[str], str]


def prune_overlapped_paragraphs(sppds: List[SPPD]) -> List[SPPD]:
    if not sppds:
        return sppds
    dropped_index_set = set()
    for i, (spp1, spp2) in enumerate(zip(sppds, sppds[1:])):
        ip1, sr1 = spp1[0], spp1[2]
        ip2, sr2 = spp2[0], spp2[2]
        if ranges_overwrapping(sr1, sr2):
            if ip1 < ip2:
                dropped_index_set.add(i)
            else:
                dropped_index_set.add(i + 1)
    return [ipsrls for i, ipsrls in enumerate(sppds) if i not in dropped_index_set]


def excerpt_text(lines: List[str], similarity_to_lines: Callable[[List[str]], float], length_to_excerpt: int) -> str:
    if not lines:
        return ""

    if len(lines) == 1:
        return lines[0][:length_to_excerpt]

    len_lines = len(lines)
    max_sim_data = None
    for p in range(len_lines):
        para_textlen = len(lines[p])
        if para_textlen == 0:
            continue  # for p
        q = p + 1
        while q < len_lines and para_textlen < length_to_excerpt:
            para_textlen += len(lines[q])
            q += 1
        sim = similarity_to_lines(lines[p:q])
        if max_sim_data is None or sim > max_sim_data[0]:
            max_sim_data = sim, (p, q)
        if q == len_lines:
            break  # for p
    assert max_sim_data is not None

    b, e = max_sim_data[1]
    excerpt = "|".join(lines[b:e])
    excerpt = excerpt[:length_to_excerpt]
    return excerpt


def trim_search_results(search_results: List[SPPD], top_n: int):
    search_results.sort(reverse=True)
    del search_results[top_n:]


def print_intermediate_search_result(search_results: List[SPPD], done_files: int, elapsed_time: float):
    if search_results:
        sim, para_len, pos, _para, df = search_results[0]
        print("%s[%d done, %.2f docs/s] cur top-1: %.4f %d %s:%d-%d" % (_ANSI_ESCAPE_CLEAR_CUR_LINE, done_files, done_files / elapsed_time, sim, para_len, df, pos[0] + 1, pos[1]), end="", file=sys.stderr)


def find_similar_paragraphs(doc_files: Iterable[str], model: Model, a: CLArgs) -> List[SPPD]:
    scanner = scanners.Scanner()

    search_results: List[SPPD] = []
    sim_min_req = 0.5
    for df in doc_files:
        # read lines from document file
        lines = scanner.scan(df)

        # for each paragraph in the file, calculate the similarity to the query
        sppds: List[SPPD] = []
        for pos in sliding_window_iter(len(lines), a.window):
            para = lines[pos[0]:pos[1]]
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
            
            sppds.append((sim, para_len, pos, lines, df))

        if not sppds:
            continue  # for df

        # pick up paragraphs for the file
        if a.paragraph_search:
            sppds = prune_overlapped_paragraphs(sppds)  # remove paragraphs that overlap
            sppds.sort(reverse=True)
            del sppds[a.top_n :]
        else:
            sppds = [max(sppds)]  # extract only the most similar paragraphs in the file

        # update search results
        search_results.extend(sppds)
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
    models: List[Model] = []
    for m in a.model.split("+"):
        s = find_model_specs(m)
        if s is None:
            sys.exit("Error: model not found: %s" % m)
        tokenizer, model_file = s.tokenizer_name, s.model_file_path
        model = SCDVModel(tokenizer, model_file)
        models.append(model)
    if len(models) >= 2:
        model = CombinedModel(models)
    else:
        model = models[0]

    # 2. query
    query_lines = [a.query]
    model.set_query(query_lines)

    count_document_files = 0
    chunk_size = 10000
    shms = None
    try:
        # search for document files that are similar to the query
        a.verbose and print("", end="", file=sys.stderr)
        search_results: List[SPPD] = []
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
            a.verbose and print(_ANSI_ESCAPE_CLEAR_CUR_LINE, file=sys.stderr)
            sys.exit(str(e))
        except KeyboardInterrupt:
            if a.verbose:
                print(
                    _ANSI_ESCAPE_CLEAR_CUR_LINE +
                    "> Interrupted. Shows the search results up to now.\n" +
                    "> number of document files: %d" % count_document_files, 
                    file=sys.stderr)

        else:
            if a.verbose:
                print(
                    _ANSI_ESCAPE_CLEAR_CUR_LINE +
                    "> number of document files: %d" % count_document_files, 
                    file=sys.stderr)

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
