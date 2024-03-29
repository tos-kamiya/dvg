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
import unicodedata

from docopt import docopt
from init_attrs_with_kwargs import InitAttrsWKwArgs
import numpy as np
from win_wildcard import expand_windows_wildcard, get_windows_shell


from .iter_funcs import chunked_iter, para_chunked_iter, sliding_window_iter
from .models import SCDVModel, do_find_model_spec, load_tokenize_func
from .scanners import Scanner, ScanError, ScanErrorNotFile, to_lines
from .search_result import (
    ANSI_ESCAPE_CLEAR_CUR_LINE,
    SLPLD,
    excerpt_text,
    trim_search_results,
    print_intermediate_search_result,
    prune_overlapped_paragraphs,
)
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
DEFAULT_TOP_K = 20
DEFAULT_WINDOW_SIZE = 20
DEFAULT_EXCERPT_CHARS = 80
DEFAULT_PREFER_LONGER_THAN = 80


class CLArgs(InitAttrsWKwArgs):
    query: Optional[str]
    query_file: Optional[str]
    file: List[str]
    verbose: bool
    model: str
    top_k: int
    top_n: Optional[int]
    paragraph_search: bool
    window: int
    include: List[str]
    exclude: List[str]
    min_length: int
    excerpt_length: int
    quote: bool
    header: bool
    workers: Optional[int]
    help: bool
    version: bool
    diagnostic: bool
    unix_wildcard: bool
    vv: bool


__doc__: str = """Document-vector Grep.

Usage:
  dvg [options] [-i TEXT]... [-e TEXT]... -m MODEL <query> <file>...
  dvg [options] [-i TEXT]... [-e TEXT]... -m MODEL -f QUERYFILE <file>...
  dvg -m MODEL --diagnostic
  dvg --help
  dvg --version

Options:
  -v, --verbose                 Verbose.
  -m MODEL, --model=MODEL       Model name.
  -k NUM, --top-k=NUM           Show top NUM files [default: {dtk}].
  -p, --paragraph-search        Search paragraphs in documents.
  -w NUM, --window=NUM          Line window size [default: {dws}].
  -f QUERYFILE, --query-file=QUERYFILE  Read query text from the file.
  -i TEXT, --include=TEXT       Requires containing the specified text.
  -e TEXT, --exclude=TEXT       Requires not containing the specified text.
  -l CHARS, --min-length=CHARS  Paragraphs shorter than this get a penalty [default: {dplt}].
  -t CHARS, --excerpt-length=CHARS      Length of the text to be excerpted [default: {dec}].
  -q, --quote                   Show text instead of excerpt.
  -H, --header                  Print the header line.
  -j WORKERS, --workers=WORKERS         Worker process.
  --diagnostic                  Check model installation.
  -u, --unix-wildcard           Use Unix-style pattern expansion on Windows.
  --vv                          Show name of each input file (for debug).
  -n NUM, --top-n=NUM           Show top NUM files (same as option -k).
""".format(
    dtk=DEFAULT_TOP_K, dws=DEFAULT_WINDOW_SIZE, dplt=DEFAULT_PREFER_LONGER_THAN, dec=DEFAULT_EXCERPT_CHARS
)


def do_extract_query_lines(query: Optional[str], query_file: Optional[str]) -> List[str]:
    if query == "-" or query_file == "-":
        lines = sys.stdin.read().splitlines()
    elif query_file is not None:
        scanner = Scanner()
        try:
            lines = scanner.scan(query_file)
        except ScanError as e:
            sys.exit("Error in reading query file: %s" % e)
        finally:
            del scanner
    elif query is not None:
        lines = to_lines(query)
    else:
        assert False, "both query and query_file are None"
    return lines


def expand_file_iter(target_files: Iterable[str], windows_style: bool = False) -> Iterator[str]:
    if windows_style and get_windows_shell() is not None:
        for f in target_files:
            if f == "-":
                for L in sys.stdin:
                    L = L.rstrip()
                    yield L
            else:
                for gf in expand_windows_wildcard(f):
                    if os.path.isfile(gf):
                        yield gf
    else:
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


def find_similar_paragraphs(doc_files: Iterable[str], model: SCDVModel, a: CLArgs) -> List[SLPLD]:
    scanner = Scanner()

    search_results: List[SLPLD] = []
    sim_min_req = 0.5
    for df in doc_files:
        if a.vv:
            print(ANSI_ESCAPE_CLEAR_CUR_LINE + "[Warning] reading: %s" % df, file=sys.stderr, flush=True)

        # read lines from document file
        try:
            lines = scanner.scan(df)
        except ScanErrorNotFile as e:
            continue
        except ScanError as e:
            print(ANSI_ESCAPE_CLEAR_CUR_LINE + "[Warning] %s" % e, file=sys.stderr, flush=True)
            continue

        # for each paragraph in the file, calculate the similarity to the query
        slplds: List[SLPLD] = []
        for pos in sliding_window_iter(len(lines), a.window):
            para = lines[pos[0] : pos[1]]
            para_len = sum(len(L) for L in para)
            if (
                a.include
                and not includes_all_texts(para, a.include)
                or a.exclude
                and includes_any_of_texts(para, a.exclude)
            ):
                continue  # for pos, para

            sim = model.similarity_to_lines(para)
            if sim < sim_min_req:
                continue  # for pos, para

            if para_len < a.min_length:  # penalty for short paragraphs
                sim = sim * para_len / a.min_length
                if sim < sim_min_req:
                    continue  # for pos, para

            slplds.append((sim, para_len, pos, lines, df))

        if not slplds:
            continue  # for df

        # pick up paragraphs for the file
        if a.paragraph_search:
            slplds = prune_overlapped_paragraphs(slplds)  # remove paragraphs that overlap
            slplds.sort(reverse=True)
            del slplds[a.top_k :]
        else:
            slplds = [max(slplds)]  # extract only the most similar paragraphs in the file

        # update search results
        search_results.extend(slplds)
        if len(search_results) >= a.top_k * (2 if sim_min_req > 0.5 else 1):
            trim_search_results(search_results, a.top_k)
            sim_min_req = search_results[-1][0]

    trim_search_results(search_results, a.top_k)
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
        if a == "--expand-wildcard":
            file_pats = argv[i + 1 :]
            for fp in file_pats:
                print("%s:" % fp)
                for f in expand_file_iter([fp], windows_style=True):
                    print("    %s" % f)
            return

    # A charm to make ANSI escape sequences work on Windows
    if platform.system() == "Windows":
        import colorama

        colorama.init()

    # command-line analysis
    raw_args = docopt(__doc__, argv=argv, version="dvg %s" % VERSION)
    a = CLArgs(_cast_str_values=True, **raw_args)

    # backward compatibility issue
    if a.top_n is not None:
        a.top_k = a.top_n

    model_spec = do_find_model_spec(a.model)
    tokenizer, model_file = model_spec.tokenizer_name, model_spec.file_path
    model = SCDVModel(tokenizer, model_file)

    # diagnostic mode
    if a.diagnostic:
        print("%s %s" % (a.model, str(model_spec)))
        print(
            "[Warning] Try to load tokenize function (may cause downloading data files).", file=sys.stderr, flush=True
        )
        load_tokenize_func(a.model)
        print("[Info] Done.", file=sys.stderr, flush=True)
        sys.exit(0)

    lines = do_extract_query_lines(a.query, a.query_file)
    model.set_query(lines)

    count_document_files = 0
    chunk_size = 10000
    shms = None
    try:
        # search for document files that are similar to the query
        if a.verbose:
            print("", end="", file=sys.stderr, flush=True)
        search_results: List[SLPLD] = []
        t0 = time()
        try:
            if a.workers and a.workers >= 2:
                shms = model_shared(model)  # load the model into shared memory for process parallel
                args_it = (
                    (dfs, model, a)
                    for dfs in para_chunked_iter(
                        expand_file_iter(a.file, windows_style=not a.unix_wildcard), chunk_size, a.workers
                    )
                )
                with Pool(processes=a.workers) as pool:
                    for srs, dfs in pool.imap_unordered(find_similar_paragraphs_i, args_it):
                        search_results.extend(srs)
                        trim_search_results(search_results, a.top_k)
                        count_document_files += len(dfs)
                        if a.verbose:
                            print_intermediate_search_result(search_results, count_document_files, time() - t0)
            else:
                for dfs in chunked_iter(expand_file_iter(a.file), chunk_size):
                    search_results.extend(find_similar_paragraphs(dfs, model, a))
                    trim_search_results(search_results, a.top_k)
                    count_document_files += len(dfs)
                    if a.verbose:
                        print_intermediate_search_result(search_results, count_document_files, time() - t0)
        except FileNotFoundError as e:
            if a.verbose:
                print(ANSI_ESCAPE_CLEAR_CUR_LINE, file=sys.stderr, flush=True)
            sys.exit(str(e))
        except KeyboardInterrupt:
            if a.verbose:
                print(
                    ANSI_ESCAPE_CLEAR_CUR_LINE + "[Warning] Interrupted. Shows the search results up to now.\n",
                    file=sys.stderr,
                    flush=True,
                )
        if a.verbose:
            print(
                ANSI_ESCAPE_CLEAR_CUR_LINE + "[Info] number of document files: %d" % count_document_files,
                file=sys.stderr,
                flush=True,
            )

        # output search results
        trim_search_results(search_results, a.top_k)
        if a.header:
            print("\t".join(["sim", "chars", "location", "text"]))
        for sim, para_len, (b, e), lines, df in search_results:
            if sim < 0.5:
                break
            para = lines[b:e]
            if a.quote:
                print("%.4f\t%d\t%s:%d-%d" % (sim, para_len, df, b + 1, e))
                for L in para:
                    L = unicodedata.normalize("NFKC", L)
                    print("> %s" % L)
                print()
            else:
                excerpt = excerpt_text(para, model.similarity_to_lines, a.excerpt_length)
                excerpt = unicodedata.normalize("NFKC", excerpt)
                print("%.4f\t%d\t%s:%d-%d\t%s" % (sim, para_len, df, b + 1, e, excerpt))
    finally:
        if shms is not None:
            model_shared_close(shms)


if __name__ == "__main__":
    main()
