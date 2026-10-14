# JAIR submission source

This directory is the conversion target for the rebuilt OtiLLM manuscript.

## Current JAIR format

JAIR states that, from spring 2025 onward, new submissions must use the new
JAIR LaTeX style distributed in the official JAIR Author Kit. The style is
ACM-based. The working source here therefore uses:

```latex
\documentclass[manuscript, screen, review]{jair}
```

Do not alter margins, typefaces, paragraph spacing, or the class file.

## Before compiling

1. Download the current JAIR Author Kit from the official JAIR formatting page
   and place the supplied `jair.cls` and any required kit files in this
   directory/Overleaf project.
2. Copy the corrected regenerated PDF figures into `figures/`.
3. Convert the six corrected CSV tables into LaTeX booktabs tables.
4. Fill the exact author affiliation, contact email, ORCID, and any journal
   metadata requested by the current kit. Do not guess these fields.
5. Verify every bibliography entry against the publisher/venue record.
6. Compile in review mode and inspect all line numbers, floats, equations,
   references, and figure descriptions.

## Important

The current source is a conversion scaffold assembled from the validated
manuscript sections. It deliberately does not modify JAIR's style and it does
not fabricate metadata that has not been confirmed.

## Source audit and fresh builds (14 October 2026)

Read `../SOURCE_AUDIT_2026_10_14.md` before treating the manuscript as ready.
The earlier uploaded PDF does not match the latest source. Numeric results
remain provisional pending the measurement checks described in that audit.

Build in a **new** output directory using the original frozen publication assets
and the unpacked supplied author kit:

```bash
python build_manuscript.py \
  --asset-dir /content/drive/MyDrive/OtiLLM_JAIR_v2/final_publication_assets \
  --kit-dir /content/JAIR_Author_Kit \
  --out-dir /content/OtiLLM_JAIR_review_build_20261014
```

The kit directory must contain `jair.cls`, `acmart.cls`, `acmdatamodel.dbx`,
`acmauthoryear.bbx` and `acmauthoryear.cbx`. `pdflatex`, `biber` and matplotlib
must be installed. The asset directory must contain the six publication CSV
files under `tables/`. The script regenerates
all five figures and the six tables, runs LaTeX/Biber, checks errors and unresolved
citations, and writes `build-provenance.json`. It never runs GPU inference.

The numerical result figures are regenerated from the supplied publication CSVs
without changing the numeric values. Labels distinguish execution coverage,
candidate-pool support and the reference NLI proxy. PDF visual review is still
required, and compilation does not resolve the scientific gaps in the audit.
