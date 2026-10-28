# technical-notes

Short technical notes by Richard Burhans: measured problems in bioinformatics infrastructure, each with the
scripts that reproduce its numbers.

| note | one line |
|---|---|
| [`busybox-sort/`](busybox-sort/) | BusyBox `sort` in biocontainers holds its whole input in memory and ignores `-S`/`-T`. Killed in the middle of a pipe, it can leave a Galaxy job green with an empty or truncated output. |

Each note has:

* `paper/`: the LaTeX source, figure script and built PDF;
* `probe/`: the scripts that produce every number in it;
* `measurements/`: their raw output, and the dated literature and issue-tracker searches.

## Building a PDF

LaTeX runs in a container, so nothing needs installing beyond Docker and `uv`:

```bash
cd busybox-sort/paper
uv run --no-project --with matplotlib python make_figure.py
docker run --rm -v "$PWD":/w -w /w texlive/texlive:latest-small latexmk -pdf -interaction=nonstopmode busybox_sort.tex
```

## License

[CC0 1.0](LICENSE): text, figures and code are dedicated to the public domain. Use them for anything, with no
permission or attribution needed.
