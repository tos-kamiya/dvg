from typing import Dict, Iterable, Iterator, List, Optional, FrozenSet, Tuple

from fnmatch import fnmatch
import importlib
from itertools import groupby
from math import floor
from multiprocessing import Pool
import os
import sys
import time

from docopt import docopt
from init_attrs_with_kwargs import InitAttrsWKwArgs
from numpy.linalg import norm

from .main import _ANSI_ESCAPE_CLEAR_CUR_LINE
from .main import DEFAULT_TOP_N, DEFAULT_WINDOW_SIZE, DEFAULT_EXCERPT_CHARS, DEFAULT_PREFER_LONGER_THAN
from .main import SPPD, chunked_iter, excerpt_text, expand_file_iter, trim_search_results, print_intermediate_search_result, prune_overlapped_paragraphs
from .main import model_shared, model_shared_close
from .iter_funcs import sliding_window_iter
from .models import SCDVModel, Vec, find_model_specs
from .scdv_embedding import sparse
from .scanners import Scanner
from .text_funcs import includes_all_texts, includes_any_of_texts


_script_dir = os.path.dirname(os.path.realpath(__file__))


VERSION = importlib.metadata.version("dvg")
DEFAULT_OVER_PRUNING = 0.5

class CLArgs(InitAttrsWKwArgs):
    build: bool
    search: bool
    ls: bool
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


__doc__: str = """Dvg with index DB.

Usage:
  dvgi --build [-w WINDOW] [-j WORKERS] -m MODEL <file>...
  dvgi [--search] [options] [-H] [-w WINDOW] [-j WORKERS] [-P RATIO] -m MODEL <query> <file>...
  dvgi --ls [-H] [-w WINDOW] [-j WORKERS] -m MODEL <file>...
  dvgi --help
  dvgi --version

Options:
  --build                       (Re-) build index DB.
  --search                      Search (default). 
  --ls                          Lookup consistency between index data and existing files.
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
  --workers=WORKERS -j WORKERS  Worker process [default: 1].
  --over-pruning=RATIO, -P RATIO        Excessive early pruning. Large values will result in **inaccurate** search results [default: {dop}].
""".format(
    dtn=DEFAULT_TOP_N, dws=DEFAULT_WINDOW_SIZE, dplt=DEFAULT_PREFER_LONGER_THAN, dec=DEFAULT_EXCERPT_CHARS, dop=DEFAULT_OVER_PRUNING,
)


class FilenameMatcher:
    def __init__(self, patterns: List[str]):
        self.matchers = []
        names = []
        for p in patterns:
            if '*' in p:
                self.matchers.append(p)
            else:
                names.append(p)
        self.name_set = frozenset(names)
    
    def match(self, filename: str) -> bool:
        for m in self.matchers:
            if fnmatch(filename, m):
                return True
        return filename in self.name_set        


def calc_clusters(lines: List[str], model: SCDVModel) -> List[Tuple[int, float]]:
    vec = model._lines_to_vec(lines)
    vec = sparse(vec)

    len_idf_wvs = model.embedder.m_shape[1]
    cluster_size = model.embedder.m_shape[0]

    cluster_norms = []
    norm_sum = 0.0
    for ci in range(cluster_size):
        n = norm(vec[ci * len_idf_wvs : (ci + 1) * len_idf_wvs])
        norm_sum += n
        cluster_norms.append((ci, n))

    if norm_sum == 0:
        return []

    cluster_norms = [(ci, n / norm_sum) for ci, n in cluster_norms]
    cluster_norms.sort(key=lambda ci_n: ci_n[1], reverse=True)
    return cluster_norms


def remove_clusters_low_norm(cluster_norms: List[Tuple[int, float]], threshold: float) -> List[Tuple[int, float]]:
    cluster_norms = cluster_norms[:]
    while cluster_norms and cluster_norms[-1][1] < threshold:
        cluster_norms.pop()

    return cluster_norms


def df_mt_iter(index_file_name: str) -> Iterator[Tuple[str, int]]:
    with open(index_file_name, "r") as inp:
        last_df_mt = None
        for L in inp:
            fields = L.rstrip().split('\t')
            df, mt, lrstr, clusters = fields
            mt = int(mt)
            df_mt = (df, mt)
            if df_mt != last_df_mt:
                yield df_mt
                last_df_mt = df_mt


def calc_df_clusters(dfs: Iterable[str], model: SCDVModel, scanner: Scanner, a: CLArgs) -> List[Tuple[str, int, Tuple[int, int], List[Tuple[int, float]]]]:
    r = []
    for df in dfs:
        try:
            df_mtime = floor(os.path.getmtime(df))
        except FileNotFoundError:
            assert False, "Removed while running dvgi?: %s" % df
        lines = scanner.scan(df)
        for pos in sliding_window_iter(len(lines), a.window):
            pos_b, pos_e = pos
            para = lines[pos_b:pos_e]
            cn = calc_clusters(para, model)
            cn = remove_clusters_low_norm(cn, 0.1)
            if cn:
                r.append((df, df_mtime, pos, cn))
    return r


def calc_df_clusters_i(a):
    return calc_df_clusters(*a)


def df_para_iter(index_file_name: str, fnmatcher: FilenameMatcher, query_c_to_n: List[float], chunk_size: int, pruning_by_cluster: float) -> Iterator[Tuple[List[Tuple[str, int, Tuple[int, int]]], int]]:
    with open(index_file_name, "r") as inp:
        df_mt_poss = []
        df_count = 0
        df = file_mt = None
        for L in inp:
            fields = L.rstrip().split('\t')
            d, m, lrstr, cns = fields

            if d != df:
                df_count += 1
                if len(df_mt_poss) >= chunk_size:
                    yield df_mt_poss, df_count
                    df_mt_poss = []
                    df_count = 0
                df = d
                if fnmatcher.match(d):
                    try:
                        file_mt = floor(os.path.getmtime(df))
                    except FileNotFoundError:
                        assert False, "Removed while running dvgi?: %s" % df
                else:
                    file_mt = None

            mt = int(m)
            if file_mt is None or abs(mt - file_mt) >= 3:
                continue  # for L

            expected_norm_contribution = 0.0
            for c in cns.split(","):
                expected_norm_contribution += query_c_to_n[int(c)]
                if expected_norm_contribution >= pruning_by_cluster:
                    break  # for c
            else:
                continue  # for L
            
            b, e = lrstr.split("-")
            pos_b, pos_e = int(b), int(e)
            df_mt_poss.append((df, mt, (pos_b, pos_e)))

        if df_mt_poss:
            yield df_mt_poss, df_count


def calc_para_similarity(df_mt_pos_it: Iterable[Tuple[str, int, Tuple[int, int]]], model, scanner: Scanner, a: CLArgs, dfc: int) -> Tuple[List[SPPD], int]:
    sim_min_req = 0.5
    sppds: List[SPPD] = []
    prev_df_mt = None
    lines = None
    for df, df_mt, pos in df_mt_pos_it:
        if (df, df_mt) != prev_df_mt:
            lines = scanner.scan(df)
            prev_df_mt = (df, df_mt)
        assert lines is not None
        para = lines[pos[0]:pos[1]]
        para_len = sum(len(L) for L in para)

        if a.include and not includes_all_texts(para, a.include) or a.exclude and includes_any_of_texts(para, a.exclude):
            continue  # for df, df_mt, pos

        sim = model.similarity_to_lines(para)

        if sim < sim_min_req:
            continue  # for df, df_mt, pos

        if para_len < a.min_length:  # penalty for short paragraphs
            sim = sim * para_len / a.min_length
            if sim < sim_min_req:
                continue  # for df, df_mt, pos

        sppds.append((sim, para_len, pos, lines, df))
    return sppds, dfc


def calc_para_similarity_i(a):
    return calc_para_similarity(*a)


def update_search_results(search_results: List[SPPD], sppds: List[SPPD], top_n: int, paragraph_search: bool):
    for df, g in groupby(sppds, key=lambda sppd: sppd[4]):
        # pick up paragraphs for the file
        sppds = list(g)
        if paragraph_search:
            sppds = prune_overlapped_paragraphs(sppds)  # remove paragraphs that overlap
            sppds.sort(reverse=True)
            del sppds[top_n :]
            search_results.extend(sppds)
        else:
            if sppds:
                search_results.append(max(sppds))  # extract only the most similar paragraphs in the file

    if len(search_results) >= top_n * 2:
        trim_search_results(search_results, top_n)


def main():
    argv = sys.argv[1:]
    raw_args = docopt(__doc__, argv=argv, version="dvg %s" % VERSION)
    a = CLArgs(_cast_str_values=True, **raw_args)

    s = find_model_specs(a.model)
    if s is None:
        sys.exit("Error: model not found: %s" % a.model)
    tokenizer, model_file = s.tokenizer_name, s.model_file_path
    index_file_name = os.path.join('.dvg', "%s.w%d.clu" % (os.path.basename(model_file), a.window))

    model = SCDVModel(tokenizer, model_file)
    scanner = Scanner()

    for f in a.file:
        try:
            np = os.path.normpath(f)
            rp = os.path.relpath(np)
        except ValueError:  # relpath() may raise a ValueError on Windows
            np = f
            rp = None
        if rp != np:
            sys.exit("Error: file must be specified by relative path: %s" % f)

    chunk_size = 10000

    if a.build:
        d = os.path.dirname(index_file_name)
        if not os.path.exists(d):
            os.mkdir(d)
        with open(index_file_name, "w") as outp:
            shms = model_shared(model)  # load the model into shared memory for process parallel
            try:
                args_it = ((dfs, model, scanner, a) for dfs in chunked_iter(expand_file_iter(a.file), chunk_size))
                with Pool(processes=a.workers) as pool:
                    for r in pool.imap_unordered(calc_df_clusters_i, args_it):
                        for df, df_mtime, pos, cn in r:
                            pos_b, pos_e = pos
                            print("%s\t%d\t%d-%d\t%s" % (df, df_mtime, pos_b, pos_e, ",".join("%d" % ci for ci, n in cn)), file=outp)
            finally:
                if shms is not None:
                    model_shared_close(shms)
    elif a.ls:
        if not os.path.exists(index_file_name):
            sys.exit("Error: index db file not found: %s" % index_file_name)

        df_tbl = dict()
        for df, mt in df_mt_iter(index_file_name):
            df_tbl.setdefault(df, []).append(mt)
        if a.header:
            print("file\tmtime\tindex")
        for df in expand_file_iter(a.file):
            try:
                df_mtime = floor(os.path.getmtime(df))
            except FileNotFoundError:
                assert False, "Removed while running dvgi?: %s" % df
            d = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(df_mtime))
            df_mtime_in_indices = df_tbl.get(df, [])
            if not df_mtime_in_indices:
                print("%s\t%s\t-" % (df, d))
            elif df_mtime in df_mtime_in_indices:
                print("%s\t%s\t=" % (df, d))
            else:
                print("%s\t%s\t!" % (df, d))
    else:
        if not os.path.exists(index_file_name):
            sys.exit("Error: index db file not found: %s" % index_file_name)

        lines = scanner.to_lines(a.query)

        query_clusters = calc_clusters(lines, model)
        query_c_to_n = [0.0] * len(query_clusters)
        for c, n in query_clusters:
            query_c_to_n[c] = n
        assert query_clusters
        fnmatcher = FilenameMatcher(a.file)

        model.set_query(lines)  # change internal data of the model

        shms = model_shared(model)  # load the model into shared memory for process parallel
        try:
            # search for document files that are similar to the query
            a.verbose and print("", end="", file=sys.stderr)
            search_results: List[SPPD] = []
            count_document_files = 0
            try:
                t0 = time.time()
                args_it = ((df_mt_poss, model, scanner, a, dfc) for df_mt_poss, dfc in df_para_iter(index_file_name, fnmatcher, query_c_to_n, chunk_size, a.over_pruning))
                with Pool(processes=a.workers) as pool:
                    for sppds, dfc in pool.imap_unordered(calc_para_similarity_i, args_it):
                        count_document_files += dfc
                        update_search_results(search_results, sppds, a.top_n, a.paragraph_search)
                        if a.verbose:
                            print_intermediate_search_result(search_results, count_document_files, time.time() - t0)
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
