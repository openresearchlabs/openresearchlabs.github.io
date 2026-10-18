#!/usr/bin/env python3
"""Tentative back-fill of the `funding` field into lahti.bib.

`funding` records which of the group's own grants a publication was
supported by, as a comma-separated list of the codes used in
~/Seafile/Team/Publication.xlsx:

    funding = {AoF330887, EUH952914}

    AoF        Academy of Finland / Research Council of Finland
    RCF/SRC    Strategic Research Council of the Research Council of Finland
    EUH        European Commission / Horizon 2020
    AFG        Alhopuro foundation grant
    TUF        Turku University Foundation
    UTUGS      Turku university graduate school
    UTUGS/DPT  UTUGS Doctoral Programme in Technology
    UTUGS/MGS  UTUGS / MATTI Graduate School

The spreadsheet has one row per publication, with the funding statement of
the paper as free text and one column per group member holding the codes of
that member's grants.  The codes of a row come from two places:

  1. the per-member columns, merged (who held the grant is not kept);
  2. the funding statement, searched for the grant numbers that occur
     anywhere in those columns -- this picks up rows where the columns were
     left empty but the statement names e.g. "grant number 330887".

Only the second kind is a guess; the report marks the entries that rely on it.
A grant of a co-author outside the group is never recorded: only numbers
already known from the columns are looked for.

An entry that already has a `funding` field is left alone, so hand
corrections survive a re-run.  The field is not printed by bib2publist.py,
and pandoc drops unknown fields, so neither the list of publications nor
data/publications/lahti.json (and hence the website) is affected.

Usage:
    add_funding.py -n     report what would be done, write nothing
    add_funding.py        write lahti.bib

Needs: openpyxl.
"""
import argparse, difflib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bib2publist import getfield  # noqa: E402
BIB = os.path.join(HERE, os.pardir, "lahti.bib")
XLSX = os.path.expanduser("~/Seafile/Team/Publication.xlsx")

# Spreadsheet rows whose title does not lead to the right entry by itself,
# keyed by the start of the normalised spreadsheet title.
MANUAL = {
    # the preprint title of the BioSIFTR paper
    "biomespecificgenomecatalogues": "EscobarZepeda2025",
    # listed twice, with the words of the title swapped; without this the
    # second row drifts to "Probabilistic early warning signals" (2021)
    "multivariateprobabilisticearlywarning": "Laitinen2022",
}

NUMBERED = re.compile(r"^(AoF|RCF/SRC|EUH|AFG|TUF)(\d+)$")


def norm(s):
    s = re.sub(r"\\[a-zA-Z]+|[{}\\'\"`^~]", "", s or "")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def entries(raw):
    """Yield (key, start, end, body) for every entry of the .bib."""
    pat = re.compile(r"@(\w+)\s*\{\s*([^,]+),", re.S)
    i = 0
    while True:
        m = pat.search(raw, i)
        if not m:
            break
        # find the entry's closing brace
        depth, k = 0, raw.index("{", m.start())
        while k < len(raw):
            if raw[k] == "{":
                depth += 1
            elif raw[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        yield m.group(2).strip(), m.start(), k + 1, raw[m.start():k + 1]
        i = k + 1


def bibfield(body, name):
    return getfield(body, name) or ""


def column_codes(cells):
    codes = []
    for c in cells:
        if c is None:
            continue
        for tok in str(c).replace("_x000D_", " ").split():
            if tok not in codes:
                codes.append(tok)
    return codes


def read_rows(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    first = header.index("Funding Information") + 1
    out = []
    for r in rows[1:]:
        if not r[0]:
            continue
        year = re.search(r"\d{4}", str(r[2] or ""))
        out.append({"title": " ".join(str(r[0]).split()),
                    "year": year.group(0) if year else "",
                    "text": str(r[first - 1] or ""),
                    "codes": column_codes(r[first:])})
    return out


def match(row, by_title, years):
    """The key of the entry a spreadsheet row is about, or None."""
    n = norm(row["title"])
    for start, key in MANUAL.items():
        if n.startswith(start):
            return key
    if n in by_title:
        return by_title[n]
    # the spreadsheet title sometimes runs on into the journal or the book
    for t, key in by_title.items():
        if len(t) > 30 and n.startswith(t):
            return key
    close = difflib.get_close_matches(n, by_title.keys(), 1, 0.8)
    if close and years[by_title[close[0]]] == row["year"]:
        return by_title[close[0]]
    return None


def order(codes):
    return sorted(codes, key=lambda c: (not NUMBERED.match(c), c))


def write_funding(raw, funding):
    """Add `funding` to the entries of `raw` named in {key: [codes]}.

    Entries that already have the field are left alone.  Returns the new
    text and the number of entries changed.
    """
    out, i, added = [], 0, 0
    for key, start, end, body in entries(raw):
        out.append(raw[i:start])
        i = end
        if key not in funding or getfield(body, "funding"):
            out.append(body)
            continue
        # sit below pubclass and borrow its alignment; "funding" is one
        # character shorter
        fm = re.search(r"\n([ \t]*)pubclass([ \t]*)=[^\n]*\n", body)
        if fm:
            line = "%sfunding%s = {%s},\n" % (fm.group(1), fm.group(2),
                                              ", ".join(order(funding[key])))
            at = fm.end()
        else:
            line = "\n  funding = {%s}," % ", ".join(order(funding[key]))
            at = body.index(",", body.index("{")) + 1
        out.append(body[:at] + line + body[at:])
        added += 1
    out.append(raw[i:])
    return "".join(out), added


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="report what would be done, write nothing")
    ap.add_argument("-x", "--xlsx", default=XLSX)
    ap.add_argument("-b", "--bib", default=BIB)
    args = ap.parse_args()

    raw = open(args.bib, encoding="utf-8").read()
    by_title, years, has = {}, {}, set()
    for key, _, _, body in entries(raw):
        by_title[norm(bibfield(body, "title"))] = key
        years[key] = (re.search(r"\d{4}", bibfield(body, "year")) or [""])[0]
        if re.search(r"^\s*funding\s*=", body, re.M | re.I):
            has.add(key)

    rows = read_rows(args.xlsx)
    # grant number -> code, from the per-member columns of the whole sheet
    known = {}
    for row in rows:
        for c in row["codes"]:
            m = NUMBERED.match(c)
            if m:
                known[m.group(2)] = c

    funding, guessed, unmatched, nothing = {}, {}, [], []
    for row in rows:
        key = match(row, by_title, years)
        if key is None:
            unmatched.append(row)
            continue
        from_text = [code for num, code in known.items()
                     if re.search(r"(?<!\d)%s(?!\d)" % num, row["text"])
                     and code not in row["codes"]]
        codes = row["codes"] + from_text
        if not codes:
            nothing.append(key)
            continue
        if from_text:
            guessed.setdefault(key, []).extend(from_text)
        funding.setdefault(key, [])
        funding[key] += [c for c in codes if c not in funding[key]]

    new, added = write_funding(raw, funding)

    for key in sorted(funding):
        if key in has:
            continue
        mark = "  (from the statement: %s)" % ", ".join(order(guessed[key])) \
            if key in guessed else ""
        print("%-28s %s%s" % (key, ", ".join(order(funding[key])), mark))
    print()
    for row in unmatched:
        print("no entry for: %s (%s)" % (row["title"][:70], row["year"]))
    print("%d rows; funding %s %d entries (%d rely on the statement), "
          "%d already had it, %d rows name none of the group's grants, "
          "%d rows matched no entry"
          % (len(rows), "would be added to" if args.dry_run else "added to",
             added, sum(1 for k in guessed if k not in has),
             sum(1 for k in funding if k in has), len(nothing), len(unmatched)))

    if not args.dry_run:
        open(args.bib, "w", encoding="utf-8").write(new)


if __name__ == "__main__":
    sys.exit(main())
