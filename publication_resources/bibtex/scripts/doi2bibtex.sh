#!/usr/bin/env bash

# Returns a BibTeX (www.bibtex.org) entry for one or more given DOIs
# (https://www.doi.org/).
#
# Call it like this:
#
# $ doi2bibtex.sh 10.1093/bioinformatics/btu533
#
# Can also be used for several DOIs at once:
#
# $ doi2bibtex.sh 10.1093/bioinformatics/btu533 10.1038/sj.embor.7400538

for DOI in "$@"
do
    curl -H "Accept: application/x-bibtex" https://data.crossref.org/${DOI}
    echo ""
done