[![Tests](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml) [![CodeQL](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml)

&rarr; doc [main](https://github.com/tos-kamiya/dvg/) | [dev](https://github.com/tos-kamiya/dvg/tree/dev)  
&rarr; Japanese doc [main](https://github.com/tos-kamiya/dvg/blob/main/README.ja_JP.md) | [dev](https://github.com/tos-kamiya/dvg/blob/dev/README.ja_JP.md)  

⚠️ Warning: `dvg` is **incomplatible with CPython 3.11**, because some of its dependencyies are so. Reference: Python 3.11 Readiness [https://pyreadiness.org/3.11/](https://pyreadiness.org/3.11/)  

⚠️ Warning: In version 1.0.0b9, the model files have been revamped and now have a larger vocabulary and (vector) dimension. Due to PyPI space limitations, model files are not included in the distribution package; they are **downloaded from a website (https://toshihirokamiya.com/) at the first time you run `dvg`**.  

# dvg

The `dvg` is an off-the-shelf grep-like tool that performs semantic similarity search, for Windows, macOS, and Ubuntu.

With SCDV models, search document files that contain similar parts to query.
Supports searching within text files (.txt), PDF files (.pdf), and MS Word files (.docx).

## Installation

Basically, it can be installed with `pip dvg`, but if you want to target PDF files or Japanese documents in addition to English, you need to install an option.

&rarr; [Installation on Ubuntu / macOS](docs/installation-on-ubuntu.md)  
&rarr; [Installation on Windows](docs/installation-on-windows.md)  

## TL;DR (typical usage)

Search for the document files similar to the query phrase.

```sh
dvg -v -m en <query_phrase> <document_files>...
```

Example of search:  
![](docs/images/run1.png)

Each line of output is, from left to right, similarity (the closer the number is to 1, the higher the similarity), length (characters) of the paragraph, file name, and range of line numbers.

## Command-line options

`dvg` has several options. Here are some options that may be used frequently.

`-v, --verbose`  
Verbose option. If specified, it will show the documents that have the highest similarity at that time.

`-m MODEL, --model=MODEL`  
The available models are `en` (for English documents) and `ja` (for Japanese documents).

`-n NUM, --top-n=NUM`  
Show top NUM documents as results. The default value is 20.
Specify `0` to show all the documents searched, sorted by the degree of match to the query.

`-p, --paragraph`  
If this option is specified, each paragraph in one document file will be considered as a document. Multiple paragraphs of a single document file will be output in the search results.
If this option is not specified, one document file will be considered as one document. A single document file will be displayed in the search results only once at most.

`-w NUM, --window=NUM`  
A chunk of lines specified by this number will be recognized as a paragraph.
The default value is 20.

`-f QUERYFILE, --query-file=QUERYFILE`  
Read query text from the file.
The query file could be a PDF as well as a text file, like document files.

(As far as I have tried, when the query is specified as a file, better results tend to be obtained by increasing the size of the paragraph with the --window option, e.g. `-w 80`)

`-i TEXT, --include=TEXT`  
Only paragraphs that contain the specified string will be included in the search results.

`-e TEXT, --exclude=TEXT`  
Only paragraphs that do not contain the specified string will be included in the search results.

`-l CHARS, --min-length=CHARS`  
Paragraphs shorter than this value get their similarity values lowered. You can use this to exclude short paragraphs from the search results. The default value is 80.

`-t CHARS, --excerpt-length=CHARS`  
The length of the excerpt displayed in the rightmost column of the search results. The default value is 80.

`-q, --quote`  
Show the entire paragraph (without excerpts) of search results.

`-H, --header`  
Add a heading line to the output.

`-j NUM, --worker=NUM`  
Number of worker processes. Option to run in parallel.

## Hints

&rarr; [Search individual lines of a text file](docs/search-individual-lines.md)

## Troubleshooting

&rarr; [An error message like: "ModuleNotFoundError: No module named 'docopt'"](docs/troubleshooting.md#no-docopt)

&rarr; [An error message like "dvg: command not found ".](docs/troubleshooting.md#command-not-found)

&rarr; [A warning message "None of PyTorch, TensorFlow >= 2.0, or Flax have been found..."](docs/troubleshooting.md#none-of-pytorch)

&rarr; [Aborted by segmentation fault (SIGSEGV)](docs/troubleshooting.md#segfault)

## Acknowledgements

Thanks to Wikipedia for releasing a huge corpus of languages:  
https://dumps.wikimedia.org/

## License

dvg is distributed under [BSD-2](https://opensource.org/licenses/BSD-2-Clause) license.

## Links

* PyPI page https://pypi.org/project/dvg/

* D. Mekala et al., "SCDV: Sparse Composite Document Vectors using soft clustering over distributional representations," https://arxiv.org/abs/1612.06778

