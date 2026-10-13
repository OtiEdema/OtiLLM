# JAIR submission source

This directory is the conversion target for the rebuilt OtiLLM manuscript.

## Current JAIR format

JAIR states that, from spring 2025 onward, new submissions must use the new
JAIR LaTeX style distributed in the official JAIR Author Kit. The style is
ACM-based. The working source here therefore uses:

```latex
\\documentclass[review]{jair}
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
