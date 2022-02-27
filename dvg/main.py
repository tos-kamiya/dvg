from typing import Callable, Iterable, Iterator, List, Optional, Tuple

from glob import glob
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

from .iter_funcs import chunked, ranges_overwrapping
from .text_funcs import extract_para_iter, includes_all_texts, includes_any_of_texts
from .models import Model, SCDVModel, CombinedModel, Vec, find_file_in_model_dir, inner_product_n, build_model_files
from . import parsers


_script_dir = os.path.dirname(os.path.realpath(__file__))


def model_shared(model: Model):
    shms =[]
    if isinstance(model, CombinedModel):
        for m in model.models:
            shms.extend(model_shared(m))
    elif isinstance(model, SCDVModel):
        model.tokenizer = None

        emb = model.embedder
        
        clusters = emb.clusters
        shmc = SharedMemory(create=True, size=clusters.nbytes)
        clusters_shared = np.ndarray(clusters.shape, dtype=clusters.dtype, buffer=shmc.buf)
        clusters_shared[:] = clusters[:]
        emb.clusters = clusters_shared
        shms.append(shmc)

        idf_wvs = emb.idf_wvs
        shmv = SharedMemory(create=True, size=idf_wvs.nbytes)
        idf_wvs_shared = np.ndarray(idf_wvs.shape, dtype=idf_wvs.dtype, buffer=shmv.buf)
        idf_wvs_shared[:] = idf_wvs[:]
        emb.idf_wvs = idf_wvs_shared
        shms.append(shmv)
    return shms


def model_shared_close(shms):
    for shm in shms:
        shm.close()
        shm.unlink()


VERSION = importlib.metadata.version("dvg")
DEFAULT_TOP_N = 20
DEFAULT_WINDOW_SIZE = 20
DEFAULT_HEADLINE_CHARS = 80
DEFAULT_PREFER_LONGER_THAN = 80
_ANSI_ESCAPE_CLEAR_CUR_LINE = "\x1b[1K\n\x1b[1A"


class CLArgs(InitAttrsWKwArgs):
    query: str
    file: List[str]
    verbose: bool
    model: str
    top_n: int
    paragraph: bool
    window: int
    include: List[str]
    exclude: List[str]
    prefer_longer_than: int
    headline_length: int
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
  --top-n=NUM, -t NUM           Show top NUM files [default: {dtn}].
  --paragraph, -p               Search paragraphs in documents.
  --window=NUM, -w NUM          Line window size [default: {dws}].
  --include=TEXT, -i TEXT       Requires containing the specified text.
  --exclude=TEXT, -e TEXT       Requires not containing the specified text.
  --prefer-longer-than=CHARS, -l CHARS  Paragraphs shorter than this get a penalty [default: {dplt}].
  --headline-length=CHARS, -a CHARS     Length of headline [default: {dhc}].
  --workers=WORKERS -j WORKERS  Worker threads.
""".format(dtn=DEFAULT_TOP_N, dws=DEFAULT_WINDOW_SIZE, dplt=DEFAULT_PREFER_LONGER_THAN, dhc=DEFAULT_HEADLINE_CHARS)


def expand_file_iter(target_files: Iterable[str]) -> Iterator[str]:
    for f in target_files:
        if f == '-':
            for L in sys.stdin:
                L = L.rstrip()
                yield L
        elif "*" in f:
            gfs = glob(f, recursive=True)
            for gf in gfs:
                if os.path.isfile(gf):
                    yield gf
        else:
            yield f


Pos = Tuple[int, int]
SPP = Tuple[float, Pos, List[str]]


def prune_overlapped_paragraphs(spps: List[SPP]) -> List[SPP]:
    if not spps:
        return spps
    dropped_index_set = set()
    for i, (spp1, spp2) in enumerate(zip(spps, spps[1:])):
        ip1, sr1 = spp1[0], spp1[1]
        ip2, sr2 = spp2[0], spp2[1]
        if ranges_overwrapping(sr1, sr2):
            if ip1 < ip2:
                dropped_index_set.add(i)
            else:
                dropped_index_set.add(i + 1)
    return [ipsrls for i, ipsrls in enumerate(spps) if i not in dropped_index_set]


def extract_headline(lines: List[str], lines_to_vec: Callable[[List[str]], Vec], query_vec: Vec, headline_len: int) -> str:
    if not lines:
        return ""

    if len(lines) == 1:
        return lines[0][:headline_len]

    len_lines = len(lines)
    max_ip_data = None
    for p in range(len_lines):
        para_textlen = len(lines[p])
        q = p + 1
        while q < len_lines and para_textlen < headline_len:
            para_textlen += len(lines[q])
            q += 1
        vec = lines_to_vec(lines[p:q])
        ip = inner_product_n(vec, query_vec)
        if max_ip_data is None or ip > max_ip_data[0]:
            max_ip_data = ip, (p, q)
    assert max_ip_data is not None

    sr = max_ip_data[1]
    headline_text = "|".join(lines[sr[0] : sr[1]])
    headline_text = headline_text[:headline_len]
    return headline_text


def trim_search_results(search_results: List[Tuple[SPP, str]], top_n: int):
    search_results.sort(reverse=True)
    del search_results[top_n:]


def print_intermediate_search_result(search_results: List[Tuple[SPP, str]], done_files: int, elapsed_time: float):
    (_sim, pos, _para), f = search_results[0]
    print("%s[%d done, %.2f docs/s] cur top-1: %s:%d-%d" % (_ANSI_ESCAPE_CLEAR_CUR_LINE, done_files, done_files / elapsed_time, f, pos[0] + 1, pos[1] + 1),
        end='', file=sys.stderr)


def find_similar_paragraphs(query_vec: Vec, doc_files: Iterable[str], model: Model, a: CLArgs, verbose: bool = False) -> List[Tuple[SPP, str]]:
    parser = parsers.Parser()

    t0 = time()
    search_results: List[Tuple[SPP, str]] = []
    for dfi, df in enumerate(doc_files):
        # read lines from document file
        lines = parser.parse(df)

        # for each paragraph in the file, calculate the similarity to the query
        spps: List[SPP] = []
        for pos, para in extract_para_iter(lines, a.window):
            if a.include and not includes_all_texts(para, a.include):
                continue  # for pos, para
            if a.exclude and includes_any_of_texts(para, a.exclude):
                continue  # for pos, para
            
            vec = model.lines_to_vec(para)
            sim = inner_product_n(vec, query_vec)

            if a.prefer_longer_than > 0:  # penalty for short paragraphs
                r = sum(len(L) for L in para) / a.prefer_longer_than
                if r < 1.0:
                    sim *= r

            spps.append((sim, pos, para))
        if not spps:
            continue  # for dfi, df

        if a.paragraph:
            spps = prune_overlapped_paragraphs(spps)  # remove paragraphs that overlap
        else:
            spps = [sorted(spps).pop()]  # extract only the most similar paragraphs in the file

        # update search results
        spps.sort(reverse=True)
        del spps[a.top_n:]
        if len(search_results) < a.top_n:
            search_results.extend((spp, df) for spp in spps)
        else:
            if search_results[-1][0][0] < spps[0][0]:
                search_results.extend((spp, df) for spp in spps)

        trim_search_results(search_results, a.top_n)
        if verbose and dfi % 100 == 0:
            print_intermediate_search_result(search_results, dfi + 1, time() - t0)

    return search_results


def find_similar_paragraphs_i(a):
    return find_similar_paragraphs(*a)


def main():
    # A charm to make ANSI escape sequences work on Windows
    if platform.system() == "Windows":
        import colorama
        colorama.init()

    # post-installatino hook
    build_model_files()

    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--bin-dir":
            print(os.path.join(_script_dir, "bin"))
            return

    # command-line analysis
    argv = sys.argv[1:]
    raw_args = docopt(__doc__, argv=argv, version="dvg %s" % VERSION)
    a = CLArgs(_cast_str_values=True, **raw_args)

    # 1. model
    models: List[Model] = []
    for m in a.model.split('+'):
        m0 = m
        if not m.endswith('.pkl'):
            m = m + '.pkl'
        if not os.path.exists(m):
            m = find_file_in_model_dir(m)
            if not m:
                sys.exit("Error: model not found: %s" % m0)
        model = SCDVModel('ja', m)
        models.append(model)
    if len(models) >= 2:
        model = CombinedModel(models)
    else:
        model = models[0]

    # 2. query
    query_vec = model.lines_to_vec([a.query])

    # optimize the model from a given query.
    model.optimize_for_query_vec(query_vec)
    query_vec = model.lines_to_vec([a.query])

    chunk_size = 10000
    shms = None
    try:
        # search for document files that are similar to the query
        a.verbose and print("", end='', file=sys.stderr)
        search_results: List[Tuple[SPP, str]] = []
        try:
            if a.workers and a.workers >= 2:
                shms = model_shared(model)  # load the model into shared memory for process parallel
                with Pool(processes=a.workers) as pool:
                    t0 = time()
                    args_it = ((query_vec, dfs, model, a) for dfs in chunked(expand_file_iter(a.file), chunk_size))
                    for ci, srs in enumerate(pool.imap_unordered(find_similar_paragraphs_i, args_it)):
                        search_results.extend(srs)
                        trim_search_results(search_results, a.top_n)
                        if a.verbose:
                            print_intermediate_search_result(search_results, (ci + 1) * chunk_size, time() - t0)
            else:
                def chain_chunk_iter(chunk_it):
                    for chunk in chunk_it:
                        for item in chunk:
                            yield item
                df_it = chain_chunk_iter(chunked(expand_file_iter(a.file), chunk_size))
                search_results: List[Tuple[SPP, str]] = find_similar_paragraphs(query_vec, df_it, model, a, verbose=a.verbose)
        except FileNotFoundError as e:
            a.verbose and print(_ANSI_ESCAPE_CLEAR_CUR_LINE, file=sys.stderr)
            sys.exit(str(e))
        except KeyboardInterrupt:
            a.verbose and print(_ANSI_ESCAPE_CLEAR_CUR_LINE, file=sys.stderr)
            print("> Interrupted. Shows the search results up to now.", file=sys.stderr)
        else:
            a.verbose and print(_ANSI_ESCAPE_CLEAR_CUR_LINE, file=sys.stderr)

        # output search results
        trim_search_results(search_results, a.top_n)
        for spp, df in search_results:
            sim, pos, para = spp
            if sim < 0.0:
                break
            headline = extract_headline(para, model.lines_to_vec, query_vec, a.headline_length)
            print("%g\t%d\t%s:%d-%d\t%s" % (sim, sum(len(L) for L in para), df, pos[0] + 1, pos[1] + 1, headline))
    finally:
        if shms is not None:
            model_shared_close(shms)


if __name__ == "__main__":
    main()
