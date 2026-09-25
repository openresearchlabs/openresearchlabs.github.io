# Detecting new publications from email

Run this alongside `publist_candidates.py`. ORCID is the better source and
needs no mailbox access, so start there; email earns its place by carrying
things ORCID cannot know yet — acceptances, submissions, and papers whose
DOI has not yet propagated.

This is a runbook rather than a script because reading a mailbox needs the
Gmail connector, not a shell. Give it to a scheduled agent, or follow it by
hand.

## 1. Search

Publisher article-status mail, which is where a real publication shows up:

    newer_than:90d ({from:elsevier.com OR from:nature.com OR from:springer.com
      OR from:wiley.com OR from:oup.com OR from:frontiersin.org
      OR from:mdpi.com OR from:biomedcentral.com OR from:plos.org
      OR from:biorxiv.org OR from:medrxiv.org}
      OR subject:{"share your article" "now published" "has been published"
                  "accepted for publication" "your article" proof})

Journal office mail, which catches a manuscript months earlier:

    newer_than:90d subject:{"receipt of new" "co-author" "manuscript"
                            "has been submitted" "decision"}

## 2. Keep and discard

Keep:

  - "Share your article [CLNESP_105108] published in Clinical Nutrition ESPEN"
    -- an Elsevier article ID; the DOI is 10.1016/j.<journal>.<year>.<id>
  - "now published", "has been published", "accepted for publication"
  - "Receipt of New Paper by <journal>" naming LL as co-author -- a
    SUBMISSION. Not published, so not an entry yet, but worth knowing: it
    becomes `pubstate = {submitted}` if you track those.

Discard, they carry no new work:

  - ResearchGate "someone just recommended your article" -- these are about
    papers you already have, and they are the bulk of the volume
  - Google Scholar citation alerts -- papers citing you, not by you
  - reviewer certificates, Scopus access, conference calls, marketing

## 3. Extract

Pull DOIs with `10\.\d{4,9}/[^\s<>")]+` from the body, strip trailing
punctuation, and lowercase. Where a publisher gives an article ID rather
than a DOI, resolve the title through Crossref instead:

    https://api.crossref.org/works?rows=3&query.bibliographic=<title>&query.author=Lahti

Write one DOI per line to `email-dois.txt`.

## 4. Hand over

    python3 publist_candidates.py --extra-dois email-dois.txt -o candidates.bib

The same filters then apply: anything already in lahti.bib by DOI or title,
any conference abstract, any correction, and anything without LL in the
author list is dropped, with the reason printed.

## 5. Review

`candidates.bib` is a draft, never a commit. Every entry carries TODO lines
for the fields metadata cannot decide: `pubclass`, `keywords`, and `group`
for software. Move the entries you want into lahti.bib by hand, then run
`publication-list.sh` and push.
