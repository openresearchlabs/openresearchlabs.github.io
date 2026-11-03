#!/usr/bin/env python3
"""List DOIs of recent works with a Lahti among the authors.

    python3 recent_dois.py [--days 60] > recent-dois.txt

ORCID only knows what has been claimed there, which lags for preprints and
fresh articles. This asks the sources directly:

  - Crossref, by ORCID and by author name: journal articles, and
    bioRxiv/medRxiv preprints, which register their DOIs with Crossref
  - arXiv, by author: its DOIs are 10.48550/arXiv.<id>

The net is wide on purpose. Every DOI goes on to publist_candidates.py,
which drops what is already recorded and anything without Lahti in the
author list; what is left is still read by a person before it is filed.
"""
import argparse, datetime, json, re, subprocess, sys
from urllib.parse import quote

UA = "publist-candidates (mailto:leo.lahti@iki.fi)"
ORCID = "0000-0001-5537-637X"


def fetch(url):
    cmd = ["curl", "-sS", "-m", "60", "-L", "-H", "User-Agent: " + UA, url]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def crossref_items(query):
    url = ("https://api.crossref.org/works?rows=200&select=DOI,author&" + query)
    try:
        return json.loads(fetch(url))["message"]["items"]
    except Exception as e:
        sys.stderr.write("crossref: %s\n" % e)
        return []


def crossref(since):
    # works that carry LL's ORCID: exact, but only where the publisher sent it
    tagged = crossref_items("filter=orcid:%s,from-created-date:%s" % (ORCID, since))
    items = crossref_items("query.author=%s&filter=from-created-date:%s"
                           % (quote("Leo Lahti"), since))
    # query.author ranks rather than filters, and Lahti is a common name:
    # keep an L. Lahti whose ORCID, when Crossref has one, is LL's
    def me(a):
        orcid = (a.get("ORCID") or "").rsplit("/", 1)[-1]
        return ((a.get("family") or "").lower() == "lahti"
                and (a.get("given") or "").upper().startswith("L")
                and orcid in ("", ORCID))
    return [i["DOI"].lower() for i in tagged] + [
        i["DOI"].lower() for i in items
        if any(me(a) for a in i.get("author") or [])]


def arxiv(since):
    url = ("http://export.arxiv.org/api/query?search_query=au:Lahti_L"
           "&sortBy=submittedDate&sortOrder=descending&max_results=50")
    out = []
    for entry in re.findall(r"<entry>(.*?)</entry>", fetch(url), re.S):
        published = re.search(r"<published>(\d{4}-\d\d-\d\d)", entry)
        ident = re.search(r"<id>https?://arxiv.org/abs/([^<v]+)", entry)
        if published and ident and published.group(1) >= since:
            out.append("10.48550/arxiv." + ident.group(1).lower())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=60)
    args = ap.parse_args()
    since = (datetime.date.today() - datetime.timedelta(days=args.days)).isoformat()
    found = crossref(since) + arxiv(since)
    sys.stderr.write("%d DOIs since %s\n" % (len(set(found)), since))
    for d in sorted(set(found)):
        print(d)


if __name__ == "__main__":
    main()
