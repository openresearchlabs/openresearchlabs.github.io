#!/usr/bin/env python3
"""Find publications that are not yet in lahti.bib.

    python3 publist_candidates.py [--extra-dois FILE] [-o candidates.bib]

Sources a list of DOIs, drops the ones already recorded, checks that the
author list really includes LL, and drafts a .bib entry for each survivor.
Nothing is written into lahti.bib: the drafts go to a separate file for
review, because the fields that decide where an entry is filed -- pubclass,
keywords, group -- are judgement calls that metadata cannot make.

ORCID is the default source: it ingests from Crossref and DataCite, so it
needs no parsing and no credentials. `--extra-dois` takes one DOI per line,
which is how DOIs harvested from email are fed in.

A candidate is skipped when it is:
  - already in lahti.bib, by DOI or by title
  - a conference abstract, unless it is a full proceedings paper
  - a correction, erratum or author correction
  - a preprint of something already recorded
Every skip is reported with its reason, so the rules can be argued with.
"""
import argparse, html, json, os, re, subprocess, sys, time, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(HERE, os.pardir, "lahti.bib")
ORCID = "0000-0001-5537-637X"
ME = "Lahti"
UA = "publist-candidates (mailto:leo.lahti@iki.fi)"


# ----------------------------------------------------------------- helpers

def fetch(url, accept=None):
    cmd = ["curl", "-sS", "-m", "30", "-L", "-H", "User-Agent: " + UA]
    if accept:
        cmd += ["-H", "Accept: " + accept]
    return subprocess.run(cmd + [url], capture_output=True, text=True).stdout


def norm(s):
    s = html.unescape(html.unescape(s or ""))     # some feeds double-escape
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"<[^>]+>", " ", s)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())


def bib_entries(path):
    raw = open(path, encoding="utf-8").read()
    out, i = [], 0
    pat = re.compile(r"@(\w+)\s*\{\s*([^,\n]+),")
    while True:
        m = pat.search(raw, i)
        if not m:
            break
        depth, k = 0, raw.index("{", m.start())
        while k < len(raw):
            if raw[k] == "{":
                depth += 1
            elif raw[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out.append(raw[m.start():k + 1])
        i = k + 1
    return out


def field(block, name):
    m = re.search(r"^\s*" + name + r"\s*=\s*", block, re.M | re.I)
    if not m:
        return None
    p = m.end()
    if p < len(block) and block[p] == "{":
        depth, q = 0, p
        while q < len(block):
            if block[q] == "{":
                depth += 1
            elif block[q] == "}":
                depth -= 1
                if depth == 0:
                    break
            q += 1
        return re.sub(r"[{}]", "", block[p + 1:q])
    m2 = re.match(r"[^,\n]+", block[p:])
    return m2.group(0).strip() if m2 else None


# -------------------------------------------------------------- the filters

CORRECTION = re.compile(r"^\s*(author\s+)?(correction|corrigendum|erratum|"
                        r"retraction|publisher\s+correction)\b", re.I)
# a poster or session code opening the title: PWE-361, OP0123, P-45
POSTER_CODE = re.compile(r"^\s*[A-Z]{1,4}[-\s]?\d{2,5}\b")
ABSTRACT_ISSUE = re.compile(r"suppl|oce|abstract", re.I)
# A369.1, e210: abstract pagination rather than a page range
ABSTRACT_PAGE = re.compile(r"^(A\d|e\d+$)", re.I)


def is_shouted(title):
    letters = [c for c in re.sub(r"<[^>]+>", "", title or "") if c.isalpha()]
    if len(letters) < 12:
        return False
    return sum(c.isupper() for c in letters) / len(letters) > 0.75


def abstract_reason(c):
    """Why this looks like a conference abstract, or None."""
    title = (c.get("title") or "")
    issue = str(c.get("issue") or "")
    page = str(c.get("page") or "")
    container = (c.get("container-title") or "")
    if ABSTRACT_ISSUE.search(issue):
        return "supplement issue %r" % issue
    if ABSTRACT_PAGE.match(page):
        return "abstract pagination %r" % page
    if POSTER_CODE.match(title):
        return "title opens with a poster code"
    if is_shouted(title):
        return "title is all capitals"
    if re.search(r"conference series|abstracts?$", container, re.I):
        return "venue is an abstract series"
    return None


def classify(c, bib_dois, bib_titles):
    """(verdict, reason). verdict is 'propose' or 'skip'."""
    doi = (c.get("DOI") or "").lower()
    title = c.get("title") or ""
    if doi in bib_dois:
        return "skip", "already in the file"
    if norm(title) and norm(title) in bib_titles:
        return "skip", "already in the file under another DOI"
    if not any(ME.lower() == (a.get("family") or "").lower()
               for a in (c.get("author") or [])):
        return "skip", "no %s in the author list" % ME
    if CORRECTION.match(title):
        return "skip", "a correction, not a new publication"
    kind = c.get("type") or ""
    reason = abstract_reason(c)
    if reason and kind != "proceedings-article":
        return "skip", "conference abstract: " + reason
    if reason and kind == "proceedings-article":
        return "skip", "conference abstract: " + reason
    if kind == "posted-content":
        return "propose", "preprint -- check it is not a version of a recorded paper"
    return "propose", kind or "publication"


# ------------------------------------------------------------ bib drafting

def initials(given):
    return "".join(p[0].upper() for p in re.split(r"[\s.-]+", given or "") if p)


def author_field(c):
    names = []
    for a in c.get("author") or []:
        fam, giv = a.get("family"), a.get("given")
        part = a.get("dropping-particle") or a.get("non-dropping-particle")
        if not fam:
            if a.get("literal"):
                names.append("{%s}" % a["literal"])
            continue
        if part:
            fam = "%s %s" % (part, fam)
        names.append("%s, %s" % (fam, giv) if giv else "{%s}" % fam)
    return " and ".join(names)


def draft(c, verdict_note):
    doi = (c.get("DOI") or "").lower()
    parts = (c.get("issued", {}).get("date-parts") or [[None]])[0]
    year = parts[0] if parts else ""
    month = "%02d" % parts[1] if len(parts) > 1 and parts[1] else None
    fam = next((a.get("family") for a in (c.get("author") or []) if a.get("family")), "Anon")
    key = "%s%s" % (re.sub(r"[^A-Za-z]", "", unicodedata.normalize("NFKD", fam)
                           .encode("ascii", "ignore").decode()), year)
    lines = ["@article{%s," % key,
             "\t%% TODO %s" % verdict_note,
             "\t% TODO set pubclass, keywords, and group if this is software",
             "\tpubclass     = {A1},",
             "\ttitle        = {%s}," % re.sub(r"<[^>]+>", "", c.get("title") or ""),
             "\tauthor       = {%s}," % author_field(c)]
    if year:
        lines.append("\tyear         = %s," % year)
    if month:
        lines.append("\tmonth        = {%s}," % month)
    for bib_name, csl in (("journal", "container-title"), ("volume", "volume"),
                          ("number", "issue"), ("pages", "page")):
        v = c.get(csl)
        if v:
            lines.append("\t%-12s = {%s}," % (bib_name, v))
    if c.get("ISSN"):
        lines.append("\tissn         = {%s}," % c["ISSN"][0])
    lines.append("\tdoi          = {%s}," % doi)
    lines.append("\tkeywords     = {bioscience}")
    lines.append("}")
    return "\n".join(lines)


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-b", "--bib", default=BIB)
    ap.add_argument("--orcid", default=ORCID)
    ap.add_argument("--no-orcid", action="store_true",
                    help="use only the DOIs given by --extra-dois")
    ap.add_argument("--extra-dois", metavar="FILE",
                    help="one DOI per line, e.g. harvested from email")
    ap.add_argument("-o", "--output", help="write the drafts here")
    args = ap.parse_args()

    blocks = bib_entries(args.bib)
    bib_dois = {(field(b, "doi") or "").strip().lower() for b in blocks}
    bib_dois.discard("")
    bib_titles = {norm(field(b, "title")) for b in blocks}

    dois = []
    if not args.no_orcid:
        works = json.loads(fetch("https://pub.orcid.org/v3.0/%s/works" % args.orcid,
                                 "application/json"))
        for w in works.get("group", []):
            for i in (w.get("external-ids", {}).get("external-id") or []):
                if i.get("external-id-type") == "doi":
                    dois.append(i["external-id-value"].strip().lower())
    if args.extra_dois:
        for line in open(args.extra_dois, encoding="utf-8"):
            d = re.sub(r"^https?://(dx\.)?doi\.org/", "", line.strip(), flags=re.I)
            if d.startswith("10."):
                dois.append(d.lower())

    seen, todo = set(), []
    for d in dois:
        if d not in seen and d not in bib_dois:
            seen.add(d)
            todo.append(d)
    sys.stderr.write("%d DOIs from the sources, %d not already recorded\n"
                     % (len(set(dois)), len(todo)))

    proposed, skipped = [], []
    for d in todo:
        body = fetch("https://doi.org/" + d, "application/vnd.citationstyles.csl+json")
        try:
            c = json.loads(body)
        except Exception:
            skipped.append((d, "", "could not be resolved"))
            continue
        c.setdefault("DOI", d)
        if isinstance(c.get("title"), list):
            c["title"] = c["title"][0] if c["title"] else ""
        if isinstance(c.get("container-title"), list):
            c["container-title"] = c["container-title"][0] if c["container-title"] else ""
        verdict, reason = classify(c, bib_dois, bib_titles)
        (proposed if verdict == "propose" else skipped).append((d, c, reason))
        time.sleep(0.15)

    print("\n=== proposed (%d) ===" % len(proposed))
    for d, c, reason in sorted(proposed, key=lambda x: str(x[1].get("container-title"))):
        print("\n  %s  [%s]" % (d, reason))
        print("    %s" % (c.get("title") or "")[:88])
        print("    %s %s" % ((c.get("container-title") or "-")[:52],
                             (c.get("issued", {}).get("date-parts") or [[None]])[0]))

    print("\n=== skipped (%d) ===" % len(skipped))
    for d, c, reason in sorted(skipped, key=lambda x: x[2]):
        title = (c.get("title") if isinstance(c, dict) else "") or ""
        print("  %-34s %-46s %s" % (reason[:34], title[:46], d))

    if args.output and proposed:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write("%% Candidates for lahti.bib, drafted %s.\n"
                     "%% Review every TODO before moving an entry across.\n\n"
                     % time.strftime("%Y-%m-%d"))
            for d, c, reason in proposed:
                fh.write(draft(c, reason) + "\n\n")
        sys.stderr.write("wrote %s\n" % args.output)


if __name__ == "__main__":
    main()
