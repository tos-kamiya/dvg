## Indexing

**Indexing is not guaranteed to always improve search speed. Please check on a case-by-case basis.**

If you are repeatedly searching for the same document file, consider indexing the document files.

After creating an index DB, the performance of the search is boosted by pruning (filtering) the document files that are obviously not relevant to the query.
(The performance improvement comes from two things: fewer floating-point calculations to compute similarity, and fewer file IOs to read the document files).

(1) To perform indexing, make the directory where the document files are located the current directory and execute the command `dvgi --build` in that directory.

```sh
dvgi --build -m en <document_files>...
```

Note that the name of the command has been replaced by `dvgi`. Also, the document files you specify in indexing should be all the document files that may be the target of subsequent searches.

This command will create a subdirectory `.dvg` in the current directory, where the index DB will be placed.

(2) To perform a search using the indexing DB, execute the command line with the command `dvg` replaced by `dvgi` in the same current directory as when indexing was performed.

```sh
dvgi -v -m en <query_phrase> <document_files>...
```

Example of building index DB and search with it:  
![](images/run9.png)
