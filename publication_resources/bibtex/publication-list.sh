# Regenerate the list of publications (markdown + PDF + Word) from the bibtex
# source.
#
# Source of truth: lahti.bib, in this directory.
# Everything else is generated; do not hand-edit lahti_publ.md.
#
# ---------------------------------------------------------------------------
# Adding a publication: add the entry to lahti.bib with two extra fields
#
#   pubclass  -- which section of the list it belongs to (see below)
#   keywords  -- which research page of the website it belongs to (see below)
#
# then run this script. Push lahti.bib to GitHub as well: the bibtex2json
# Action rebuilds data/publications/lahti.json, which is what the website reads.
#
# ---------------------------------------------------------------------------
# pubclass -- the Finnish publication classes, plus the pre-publication states
#
#   preprint  submitted  inpress
#   A1  Original scientific articles
#   A2  Reviews
#   A3  Reviewed contributions to books / other compilations
#   A5  Reviewed articles in conference publications
#   B   Non-refereed scientific articles
#   D   Publications intended for professional communities
#   E1  Popular articles, newspaper articles
#   G   Theses
#   I1  Audiovisual materials
#   I2  ICT programs or applications (software, datasets)
#
# pandoc ignores this field, so the website data is unaffected by it.
#
# Sections with nothing in them are skipped entirely, heading and all -- so
# once the last "inpress" entry is published, that heading disappears by
# itself. A group heading ("A Peer-reviewed scientific articles", "E ...",
# "I ...") disappears too once all of its subsections are empty.
#
# Within a section, entries are ordered newest first by year and month.
#
# ---------------------------------------------------------------------------
# entrysubtype -- what kind of thing the entry is
#
# biblatex's field for subdividing an entry type. Values in use: software,
# dataset, abstract, thesis, interview, review, perspective, report, blog,
# manuscript. A preprint is marked by pubstate instead, not here, so that the
# two do not say the same thing twice. Not to be confused with howpublished,
# which is the VENUE (CRAN,
# Bioconductor, GitHub, arXiv, Dryad, ...). A recurring mistake in this file
# was howpublished = {software}, a kind rather than a venue.
#
# ---------------------------------------------------------------------------
# Splitting a section further (currently only I2)
#
# I2 is printed under subtitles rather than as one list. Two fields decide
# where an entry lands:
#
#   entrysubtype = {software}  or  {dataset}
#   group        = {Methods and modeling}
#                  {Microbiome data science ecosystem in R/Bioconductor}
#                  {Statistical ecology}
#                  {Bioinformatics}
#                  {Computational social science}
#                  {Computational humanities}
#
# `group` applies to software only; datasets go under "Research data", and
# anything with neither field falls under "Other outputs". A subtitle with
# nothing under it is skipped, which is why "Other outputs" does not
# currently appear. The order of the subtitles is set by SUBSECTIONS in
# bib2publist.py.
#
# ---------------------------------------------------------------------------
# related -- the publication that describes a piece of software
#
#   related = {Lahti2013intcomp}
#
# A citation key from this same file. The list prints "Associated
# publication: ..." after the entry, resolving the key to a short citation,
# and warns on stderr if the key does not exist. A tool backed by a paper
# takes that paper's year rather than a repository date.
#
# ---------------------------------------------------------------------------
# date -- a span rather than a single year
#
#   year = 2023, date = {2015/2023}   ->  prints "2015-2023"
#
# Used for software that was maintained over a period, and for the blogs.
# `year` still drives the sort order, so keep it at the latest year. pandoc
# turns the span into a CSL date range, so the website shows it too; a plain
# `year = {2015-2023}` does NOT work, it silently produces no date at all.
#
# Where the spans come from:
#   CRAN           https://crandb.r-pkg.org/<pkg>/all  -- exclude the
#                  "archived" pseudo-version, it is an event, not a release
#   Bioconductor   no timeline is published; probe
#                  bioconductor.org/packages/<ver>/bioc/html/<pkg>.html
#                  for the earliest release that has it
#   GitHub only    first to last commit. Do NOT use the repo's pushed_at:
#                  it counts a push to any branch
#
# ---------------------------------------------------------------------------
# keywords -- drives the WEBSITE, not this list
#
# An entry appears on the research page of EVERY keyword it carries, so
# `keywords = {dh, openscience}` shows up on both of those pages. Each keyword
# is matched whole, and an entry is rendered once however many match:
#   bioscience   -> /research/microbiome-data-science/
#   datascience  -> /research/computational-and-data-science/
#   dh           -> /research/computational-humanities/
#   openscience  -> /research/open-science/   (currently commented out)
#   opinion      -> /research/opinion-pieces/
# A keyword that is not one of the above (thesis, blog, review, gut) places the
# entry on no page, so it works as a free tag. An entry whose keywords are all
# of that kind appears on no research page, which is usually what you want.
#
# Prefer `doi` over `url`. Where both exist the list prints the DOI, and the
# archived copy of the paper in the repo belongs in `pdf`, not a second `url`.
# Never repeat a field name: BibTeX keeps one value and discards the rest.
#
# ---------------------------------------------------------------------------
# Hand-written prose
#
# A section can open with prose instead of going straight to the entries; it
# lives in scripts/preambles/<pubclass>.md, e.g. preambles/I2.md for the
# software overview. A subsection can have one too, named after its subtitle:
# preambles/I2-research-data.md opens the "Research data" block. Edit those
# files directly -- they are not generated. A section that has a preamble but
# no entries is still printed, so prose is never silently dropped.
#
# ---------------------------------------------------------------------------
# Output formats
#
# The markdown is the real output; the PDF and the Word file are rendered from
# it by pandoc. PDF goes through xelatex, which the diacritics in the author
# names need. Both are A4 with 2 cm margins -- for the .docx that comes from
# scripts/reference.docx, which also carries the Word styles. Edit that file in
# Word to restyle the .docx; delete it and pandoc falls back to its own styles
# on US Letter.
#
# Needs: python3, pandoc, xelatex.
# ---------------------------------------------------------------------------

# This script sits next to lahti.bib, so it finds the rest relative to
# itself and works from any checkout and any working directory.
BIBDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Write lahti_publ.md, lahti_publ.pdf and lahti_publ.docx in ~/Seafile/Team/
python3 $BIBDIR/scripts/bib2publist.py -o ~/Seafile/Team/lahti_publ.md --pdf --docx

# Pick the formats you want; markdown only is the default:
# python3 $BIBDIR/scripts/bib2publist.py -o ~/Seafile/Team/lahti_publ.md
# python3 $BIBDIR/scripts/bib2publist.py -o ~/Seafile/Team/lahti_publ.md --docx

# Print to screen without writing anything (drop -o):
# python3 $BIBDIR/scripts/bib2publist.py | less

# Render to an explicit path instead of alongside the markdown:
# python3 $BIBDIR/scripts/bib2publist.py -o ~/Seafile/Team/lahti_publ.md \
#     --pdf ~/Seafile/Team/LeoLahti-publications.pdf \
#     --docx ~/Seafile/Team/LeoLahti-publications.docx

# Read a different .bib:
# python3 $BIBDIR/scripts/bib2publist.py -b /path/to/other.bib | less

# Sanity checks, both quiet when all is well:
#   - any entry missing a pubclass is reported on stderr by the command above
#   - publist_diff.py compares the .bib against the markdown, which only tells
#     you something if the markdown has been hand-edited
# python3 $BIBDIR/scripts/publist_diff.py
