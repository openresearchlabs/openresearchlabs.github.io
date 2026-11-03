#!/usr/bin/env python3
"""Fill in the `funding` field of lahti.bib from the publications themselves.

add_funding.py takes the group's grants from ~/Seafile/Team/Publication.xlsx,
which lags behind the .bib.  This script covers the entries the spreadsheet
does not: for every entry that has a DOI and no `funding` yet, it looks up
what the publication itself declares,

  Crossref      the funders and award numbers the publisher deposited
  Europe PMC    its grant list, and for open-access papers the funding and
                acknowledgement sections of the full text
  OpenAlex      its grant list

and records the group's grants found there, in the notation of
add_funding.py (`funding = {AoF330887, EUH952914}`); the codes are listed there.

Which grants are the group's is not something the sources can tell: a paper
lists the grants of every co-author.  So only numbers already known are
looked for -- those used in a `funding` field anywhere in lahti.bib, plus
GROUP_GRANTS below.  Everything else the Research Council of Finland or the
EU funded is listed at the end of the report, with the entries it occurs in
(awards seen in a single entry only with --all): if one of those is the
group's, add it to GROUP_GRANTS and run again.

Nothing is found for a paper that is neither open access nor has funders in
its publisher metadata; those entries are reported as such and need the
statement read from the paper.  An entry that already has `funding` is never
touched.

Usage:
    fetch_funding.py -n               report, write nothing
    fetch_funding.py                  write lahti.bib
    fetch_funding.py --since 2025     only entries from 2025 on
    fetch_funding.py --cache DIR      keep the downloaded records in DIR
"""
import argparse, html, json, os, re, sys, tempfile, time
import urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bib2publist import getfield  # noqa: E402
from add_funding import BIB, NUMBERED, entries, order, write_funding  # noqa: E402

# Grants of the group that no `funding` field in lahti.bib carries yet.
GROUP_GRANTS = {
    # LL's Academy of Finland postdoctoral grant; the 2013-2015 papers say
    # "Academy of Finland (grant 256950 to L.L.)"
    "256950": "AoF256950",
    # LL's grants from the Strategic Research Council of the Research
    # Council of Finland
    "352604": "RCF/SRC352604",
    "372345": "RCF/SRC372345",
}

# Bioconductor package DOIs: software landing pages, no funding metadata.
SKIP_DOI = ("10.18129/",)

AGENT = "lahti-bib-funding (https://github.com/openresearchlabs/openresearchlabs.github.io)"

# Sections of a JATS full text that carry the funding statement.
FUNDING_XML = re.compile(
    r"<funding-group.*?</funding-group>"
    r"|<ack.*?</ack>"
    r"|<(sec|notes)[^>]*>\s*<title>[^<]*(?:Fund|Acknowl|Financial|Grant)[^<]*</title>.*?</\1>"
    r'|<fn[^>]*fn-type="(?:financial-disclosure|supported-by)".*?</fn>',
    re.S | re.I)

# Funders whose other awards are worth showing for review.
REVIEW = re.compile(r"Finland|Suomen Akatemia|European Commission|Horizon|H2020"
                    r"|European Union|Alhopuro|Turku University Foundation", re.I)


def fetch(url, path):
    """The body of `url`, from `path` if it is already there."""
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", "replace")
    except Exception:          # not found, or the service is down
        text = ""
    open(path, "w", encoding="utf-8").write(text)
    time.sleep(0.15)
    return text


def as_json(text):
    try:
        return json.loads(text)
    except ValueError:
        return {}


def lookup(key, doi, cache):
    """What the publication declares: ({source: {(funder, award)}}, text)."""
    q = urllib.parse.quote(doi, safe="/")
    awards = {}

    cr = as_json(fetch("https://api.crossref.org/works/" + q,
                       os.path.join(cache, key + ".cr.json")))
    for f in cr.get("message", {}).get("funder") or []:
        for a in f.get("award") or [""]:
            awards.setdefault("Crossref", set()).add((f.get("name") or "", a))

    ep = as_json(fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                       "?query=DOI:%22" + q + "%22&format=json&resultType=core",
                       os.path.join(cache, key + ".epmc.json")))
    hit = (ep.get("resultList", {}).get("result") or [{}])[0]
    for g in (hit.get("grantsList") or {}).get("grant", []):
        awards.setdefault("Europe PMC", set()).add(
            (g.get("agency") or "", g.get("grantId") or ""))

    oa = as_json(fetch("https://api.openalex.org/works/doi:" + q,
                       os.path.join(cache, key + ".oa.json")))
    for g in (oa.get("grants") or []) + (oa.get("awards") or []):
        awards.setdefault("OpenAlex", set()).add(
            (g.get("funder_display_name") or "",
             str(g.get("award_id") or g.get("funder_award_id") or "")))

    text = ""
    if hit.get("pmcid"):
        xml = fetch("https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML"
                    % hit["pmcid"], os.path.join(cache, key + ".xml"))
        text = " ".join(m.group(0) for m in FUNDING_XML.finditer(xml))
        text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))
    return awards, text.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="report what would be done, write nothing")
    ap.add_argument("-b", "--bib", default=BIB)
    ap.add_argument("--since", type=int, default=0, metavar="YEAR",
                    help="only entries from this year on")
    ap.add_argument("--all", action="store_true",
                    help="list every other award, not only those declared "
                         "by two or more entries")
    ap.add_argument("--cache", metavar="DIR",
                    help="keep the downloaded records here and reuse them")
    args = ap.parse_args()

    raw = open(args.bib, encoding="utf-8").read()
    known = dict(GROUP_GRANTS)
    todo, no_doi = [], []
    for key, _, _, body in entries(raw):
        have = getfield(body, "funding")
        for c in (have or "").split(","):
            m = NUMBERED.match(c.strip())
            if m:
                known[m.group(2)] = c.strip()
        year = int((re.search(r"\d{4}", getfield(body, "year") or "") or ["0"])[0])
        if have or year < args.since:
            continue
        doi = (getfield(body, "doi") or "").strip()
        if not doi or doi.startswith(SKIP_DOI):
            no_doi.append(key)
        else:
            todo.append((year, key, doi))

    cache = args.cache or tempfile.mkdtemp(prefix="bib-funding-")
    os.makedirs(cache, exist_ok=True)

    funding, silent, others = {}, [], {}
    for year, key, doi in sorted(todo, reverse=True):
        awards, text = lookup(key, doi, cache)
        declared = text + " " + " ".join(
            "%s %s" % pair for pairs in awards.values() for pair in pairs)
        codes = [c for n, c in known.items()
                 if re.search(r"(?<!\d)%s(?!\d)" % n, declared)]
        sources = sorted(awards) + (["full text"] if text else [])
        if codes:
            funding[key] = codes
            print("%d %-26s %s  [%s]" % (year, key, ", ".join(order(codes)),
                                         ", ".join(sources)))
        elif not sources:
            silent.append(key)
        for pairs in awards.values():
            for funder, award in pairs:
                if not REVIEW.search(funder):
                    continue
                for n in re.findall(r"(?<!\d)\d{5,9}(?!\d)", award):
                    if n not in known:
                        others.setdefault(n, (funder, set()))[1].add(key)

    new, added = write_funding(raw, funding)
    if not args.dry_run:
        open(args.bib, "w", encoding="utf-8").write(new)

    print("\n%d entries looked up; funding %s %d of them"
          % (len(todo), "would be added to" if args.dry_run else "added to", added))
    print("%d declare funding, but none of the group's known grants"
          % (len(todo) - len(funding) - len(silent)))
    print("%d have no funding information in any source: %s"
          % (len(silent), " ".join(sorted(silent))))
    print("%d have no DOI to look up" % len(no_doi))
    if not args.all:
        others = {n: v for n, v in others.items() if len(v[1]) > 1}
    if others:
        print("\nOther Finnish and EU awards declared (not known as the group's):")
        for n, (funder, keys) in sorted(others.items(),
                                        key=lambda kv: (-len(kv[1][1]), kv[0])):
            print("  %-10s %-34s %s" % (n, funder[:34], " ".join(sorted(keys))))


if __name__ == "__main__":
    sys.exit(main())
