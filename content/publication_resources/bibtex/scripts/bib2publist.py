#!/usr/bin/env python3
"""Generate the manual "List of publications" from lahti.bib.

    python3 bib2publist.py [-o OUTPUT.md] [--pdf [OUTPUT.pdf]]

Sections and their order come from the `pubclass` field of each entry (see
add_pubclass.py).  Within a section, entries are ordered newest first.

A section can carry hand-written introductory prose: put it in
`preambles/<pubclass>.md` next to this script (e.g. `preambles/I2.md`) and it
is inserted between the section heading and its entries.

`--pdf` additionally renders the markdown through pandoc + xelatex.
"""
import argparse, os, re, shutil, subprocess, sys, unicodedata
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(HERE, os.pardir, "lahti.bib")
ME = "Lahti"                      # surname to emphasise in the author lists
PREAMBLES = os.path.join(HERE, "preambles")

# (pubclass, heading, members).  A pubclass of None makes the row a group
# heading that introduces the sections listed in `members`; it is printed only
# when at least one of those sections has something in it.  Sections with
# neither entries nor a preamble are skipped entirely, heading and all.
LAYOUT = [
    (None,        "A Peer-reviewed scientific articles",
     ("preprint", "submitted", "inpress", "A1", "A2", "A3", "A5")),
    ("preprint",  "Preprints", None),
    ("submitted", "Submitted", None),
    ("inpress",   "In press / Accepted for publication", None),
    ("A1",        "A1 Original scientific articles", None),
    ("A2",        "A2 Reviews", None),
    ("A3",        "A3 Reviewed contributions to book/other compilations", None),
    ("A5",        "A5 Reviewed articles in conference publications", None),
    ("B",         "B Non-refereed scientific articles", None),
    ("D",         "D Publications intended for professional communities", None),
    (None,        "E Publications intended for the general public", ("E1",)),
    ("E1",        "E1 Popular articles, newspaper articles", None),
    ("G",         "G Theses", None),
    (None,        "I Audiovisual materials and programs in information and "
                  "communication technology (ICT)", ("I1", "I2")),
    ("I1",        "I1 Audiovisual materials", None),
    ("I2",        "I2 ICT programs or applications", None),
]
# Sections presented as bullets with the title first; the rest are numbered
# with the authors first.
TITLE_FIRST = {"preprint", "submitted", "inpress"}
BULLETED = TITLE_FIRST | {"D", "E1", "G", "I1", "I2"}

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# --------------------------------------------------------------------- bibtex

def parse(path):
    raw = open(path, encoding="utf-8").read()
    entries, i = [], 0
    pat = re.compile(r"@(\w+)\s*\{\s*([^,]+),", re.S)
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
        entries.append({"type": m.group(1).lower(), "key": m.group(2).strip(),
                        "body": raw[m.start():k + 1]})
        i = k + 1
    for e in entries:
        for f in ("title", "author", "journal", "booktitle", "year", "doi",
                  "url", "note", "volume", "number", "issue", "pages", "month",
                  "issn", "publisher", "series", "editor", "howpublished",
                  "school", "institution", "address", "pubclass", "authorship",
                  "date"):
            e[f] = tidy(getfield(e["body"], f))
        # author needs its braces intact: they mark corporate names
        e["author_raw"] = getfield(e["body"], "author")
    return entries


def getfield(body, name):
    m = re.search(r"^\s*" + name + r"\s*=\s*", body, re.I | re.M)
    if not m:
        return None
    p = m.end()
    if p < len(body) and body[p] == "{":
        depth, q = 0, p
        while q < len(body):
            if body[q] == "{":
                depth += 1
            elif body[q] == "}":
                depth -= 1
                if depth == 0:
                    break
            q += 1
        return body[p + 1:q]
    if p < len(body) and body[p] == '"':
        return body[p + 1:body.index('"', p + 1)]
    m2 = re.match(r"[^,\n]+", body[p:])
    return m2.group(0).strip() if m2 else None


def tidy(s):
    """Strip TeX braces and escapes, collapse whitespace."""
    if s is None:
        return None
    s = re.sub(r"\\&", "&", s)
    s = re.sub(r'\\["\'`^~=.]\{?(\w)\}?', r"\1", s)   # \"{o} -> o (accents)
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    return " ".join(s.split())


# --------------------------------------------------------------- formatting

CORPORATE = re.compile(
    r"\b(consorti|challenge|communit|group|collaborat|network|committee|"
    r"coordination|society|team|action|project|initiative)", re.I)


def split_authors(field):
    """Split on ` and `, but never inside {braces}."""
    if not field:
        return []
    field = " ".join(field.split())          # newlines inside the field
    parts, start, depth = [], 0, 0
    for m in re.finditer(r"[{}]|\sand\s", field):
        tok = m.group(0)
        if tok == "{":
            depth += 1
        elif tok == "}":
            depth -= 1
        elif depth == 0:
            parts.append(field[start:m.start()])
            start = m.end()
    parts.append(field[start:])
    return [p.strip() for p in parts if p.strip()]


def is_corporate(name):
    """A fully brace-wrapped name, or one that reads like an organisation."""
    stripped = name.strip()
    if stripped.startswith("{") and stripped.endswith("}") \
            and stripped.count("{") == 1:
        return True
    return bool(CORPORATE.search(tidy(stripped)))


def initials(given):
    out = []
    for chunk in re.split(r"[\s.-]+", given):
        if chunk:
            out.append(chunk[0].upper())
    return "".join(out)


def format_author(name):
    """`Willem M. de Vos` / `Vos, Willem M. de` -> `de Vos WM`."""
    if is_corporate(name):
        return tidy(name)
    name = tidy(name)
    if "," in name:
        family, given = [x.strip() for x in name.split(",", 1)]
    else:
        words = name.split()
        # a trailing lowercase particle run belongs to the surname
        cut = len(words) - 1
        while cut > 0 and words[cut - 1][:1].islower():
            cut -= 1
        family, given = " ".join(words[cut:]), " ".join(words[:cut])
    if not given:                      # corporate author, e.g. {OpenUTU work group}
        return family
    ini = initials(given)
    label = ("%s %s" % (family, ini)).strip()
    return "**%s**" % label if family.split()[-1] == ME else label


def author_list(field):
    names = [format_author(n) for n in split_authors(field)]
    if not names:
        return ""
    if names[-1].lower().strip("*") == "others":
        names[-1] = "*et al.*"
    return ", ".join(names)


def month_name(m):
    if not m:
        return None
    m = m.strip().rstrip(".")
    if m.isdigit():
        n = int(m)
        return MONTHS[n - 1] if 1 <= n <= 12 else None
    for full in MONTHS:
        if full.lower().startswith(m[:3].lower()):
            return full
    return None


def venue(e):
    return e["journal"] or e["booktitle"] or e["series"] or e["school"] \
        or e["institution"] or e["publisher"] or e["howpublished"]


def locator(e):
    """volume(issue), pages"""
    bits = ""
    if e["volume"]:
        bits += e["volume"]
    num = e["number"] or e["issue"]
    if num:
        bits += "(%s)" % num
    if e["pages"]:
        bits += (", " if bits else "") + e["pages"].replace("--", "-")
    return bits


def when(e):
    """`2011/2015` in `date` means an ongoing work: print the span."""
    if e.get("date") and "/" in e["date"]:
        a, b = (x.strip() for x in e["date"].split("/", 1))
        if a and b:
            return "%s\u2013%s" % (a, b)
    mn, yr = month_name(e["month"]), e["year"]
    return " ".join(x for x in (mn, yr) if x)


def tail(e):
    """The trailing date / ISSN / DOI / URL run, shared by both layouts."""
    out = []
    if when(e):
        out.append(when(e) + ".")
    if e["issn"]:
        out.append("ISSN:%s." % e["issn"])
    if e["doi"]:
        out.append("DOI:%s" % e["doi"])
    elif e["url"]:
        out.append("URL: `%s`" % e["url"])
    return " ".join(out)


def render(e, title_first):
    au, ti, ve, lo = author_list(e["author_raw"]), e["title"], venue(e), locator(e)
    if title_first:
        head = "**%s**" % ti
        rest = [au if au.endswith("*et al.*") else au + "."] if au else []
        if ve:
            rest.append("*%s.*" % ve + ((" " + lo + ".") if lo else ""))
        rest.append(tail(e))
        body = " ".join(x for x in rest if x)
        return "%s\n  %s" % (head, body)

    parts = []
    if au:
        parts.append(au if au.endswith("*et al.*") else au + ".")
    parts.append(ti.rstrip(".") + ".")
    if ve:
        parts.append("*%s*%s." % (ve, (" " + lo) if lo else ""))
    elif lo:
        parts.append(lo + ".")
    parts.append(tail(e))
    if e["note"]:
        parts.append("*%s*." % e["note"].rstrip("."))
    note = authorship_note(e["authorship"])
    if note:
        parts.append("*%s*." % note)
    return " ".join(x for x in parts if x)


def authorship_note(value):
    """`first, corresponding` -> `Shared first author` / `Corresponding author`.

    Plain positional values (`first`, `second`, `pi`) carry no information the
    author list does not already show, so they are dropped.
    """
    if not value:
        return None
    v = value.lower()
    labels = []
    if "shared first" in v:
        labels.append("Shared first author")
    if "corresponding" in v:
        labels.append("Corresponding author")
    return ". ".join(labels) or None


def sort_key(e):
    try:
        y = int(re.sub(r"\D", "", e["year"] or "0") or 0)
    except ValueError:
        y = 0
    mn = month_name(e["month"])
    return (-y, -(MONTHS.index(mn) + 1 if mn else 0), e["title"] or "")


# -------------------------------------------------------------------- output

def preamble(cls):
    """Hand-written prose for a section, if preambles/<cls>.md exists."""
    path = os.path.join(PREAMBLES, "%s.md" % cls)
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read().strip()
    return [text, ""] if text else []


def build(entries, today):
    by_class = {}
    for e in entries:
        by_class.setdefault(e["pubclass"] or "?", []).append(e)

    def has_content(cls):
        """A section is worth printing if it has entries or hand-written prose."""
        return bool(by_class.get(cls)) or bool(preamble(cls))

    lines = ["#### List of publications", "",
             "Leo Lahti %s" % today.strftime("%-d.%-m.%Y"), ""]
    for cls, heading, members in LAYOUT:
        if cls is None:
            if any(has_content(m) for m in members):
                lines += ["**%s**" % heading, ""]
            continue
        if not has_content(cls):
            continue
        lines += ["**%s**" % heading, ""]
        lines += preamble(cls)
        group = sorted(by_class.get(cls, []), key=sort_key)
        bullet = cls in BULLETED
        for n, e in enumerate(group, 1):
            marker = "*" if bullet else "%d." % n
            lines += ["%s %s" % (marker, render(e, cls in TITLE_FIRST)), ""]

    unclassified = by_class.get("?", [])
    if unclassified:
        sys.stderr.write("warning: %d entries have no pubclass: %s\n"
                         % (len(unclassified),
                            ", ".join(e["key"] for e in unclassified)))
    return "\n".join(lines).rstrip() + "\n"


PANDOC_OPTS = [
    "--pdf-engine=xelatex",
    "-V", "papersize=a4",
    "-V", "geometry:margin=2cm",
    "-V", "fontsize=10pt",
    "-V", "colorlinks=true",
    "-V", "linkcolor=blue",
    "-V", "urlcolor=blue",
    "-V", "mainfont=DejaVu Serif",
    "-V", "monofont=DejaVu Sans Mono",
]


def render_pdf(md_text, pdf_path):
    """Render the markdown to PDF via pandoc + xelatex."""
    if not shutil.which("pandoc"):
        sys.exit("error: pandoc is required for --pdf")
    tmp = pdf_path + ".md"
    open(tmp, "w", encoding="utf-8").write(md_text)
    try:
        proc = subprocess.run(["pandoc", tmp, "-o", pdf_path] + PANDOC_OPTS,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            sys.exit("error: pandoc failed to build %s" % pdf_path)
    finally:
        os.remove(tmp)
    sys.stderr.write("wrote %s\n" % pdf_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-b", "--bib", default=BIB)
    ap.add_argument("-o", "--output", help="markdown output path")
    ap.add_argument("--pdf", nargs="?", const=True, default=None,
                    metavar="PDF",
                    help="also render a PDF; defaults to OUTPUT with a .pdf "
                         "suffix when -o is given")
    args = ap.parse_args()

    text = build(parse(args.bib), date.today())
    if args.output:
        open(args.output, "w", encoding="utf-8").write(text)
        sys.stderr.write("wrote %s\n" % args.output)
    elif args.pdf is None:
        sys.stdout.write(text)

    if args.pdf is not None:
        if args.pdf is True:
            if not args.output:
                sys.exit("error: --pdf needs a path, or -o to derive one from")
            pdf_path = re.sub(r"\.md$", "", args.output) + ".pdf"
        else:
            pdf_path = args.pdf
        render_pdf(text, pdf_path)


if __name__ == "__main__":
    main()
