#!/usr/bin/env python3
"""Generate the manual "List of publications" from lahti.bib.

    python3 bib2publist.py [-o OUTPUT.md] [--pdf [OUT.pdf]] [--docx [OUT.docx]]

Sections and their order come from the `pubclass` field of each entry (see
add_pubclass.py).  Within a section, entries are ordered newest first.

A section can carry hand-written introductory prose: put it in
`preambles/<pubclass>.md` next to this script (e.g. `preambles/I2.md`) and it
is inserted between the section heading and its entries.

`--pdf` and `--docx` additionally render the markdown through pandoc;
the PDF goes via xelatex, which the Unicode in the author names needs.
"""
import argparse, os, re, shutil, subprocess, sys, unicodedata
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(HERE, os.pardir, "lahti.bib")
ME = "Lahti"                      # surname to emphasise in the author lists
# pandoc turns a bracketed span into a real underline in PDF and .docx;
# markdown has no underline of its own.
MARK = "[%s]{.underline}"
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
# Sections that are split further. Each row is (category, group, subtitle);
# a group of None takes every entry of that category. Entries are matched in
# this order, and a subtitle with nothing under it is skipped like any other.
SUBSECTIONS = {
    "I2": [
        ("software", "Methods and modeling",  "Software: methods and modeling"),
        ("software", "Microbiome data science ecosystem in R/Bioconductor",
                     "Software: microbiome data science ecosystem in R/Bioconductor"),
        ("software", "Statistical ecology",   "Software: statistical ecology"),
        ("software", "Bioinformatics",        "Software: bioinformatics"),
        ("software", "Computational social science", "Software: computational social science"),
        ("software", "Computational humanities",     "Software: computational humanities"),
        ("software", None,                           "Software: other"),
        ("dataset",  None,                           "Research data"),
        (None,       None,                           "Other outputs"),
    ],
}

# Sections presented as bullets with the title first; the rest are numbered
# with the authors first.
# Every section leads with the title, then the authors and the rest.
TITLE_FIRST = {"preprint", "submitted", "inpress", "A1", "A2", "A3", "A5",
               "B", "D", "E1", "G", "I1", "I2"}
# Which sections are numbered is a separate question from how an entry is
# laid out, so this is spelled out rather than derived from TITLE_FIRST.
BULLETED = {"preprint", "submitted", "inpress", "D", "E1", "G", "I1", "I2"}

# Rendered month names. `month_name` matches on the first three letters, so a
# .bib may spell the month out, abbreviate it, or give a number.
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


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
                  "date", "entrysubtype", "group", "related", "pubstate"):
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


# LaTeX accent commands -> the matching Unicode combining mark.
ACCENTS = {'"': "\u0308", "'": "\u0301", "`": "\u0300", "^": "\u0302",
           "~": "\u0303", "=": "\u0304", ".": "\u0307"}
BRACED_ACCENTS = {"v": "\u030C", "u": "\u0306", "H": "\u030B", "c": "\u0327",
                  "k": "\u0328", "r": "\u030A", "d": "\u0323", "b": "\u0331"}
LIGATURES = [("\\ss", "ß"), ("\\AA", "Å"), ("\\aa", "å"), ("\\AE", "Æ"),
             ("\\ae", "æ"), ("\\OE", "Œ"), ("\\oe", "œ"), ("\\O", "Ø"),
             ("\\o", "ø"), ("\\L", "Ł"), ("\\l", "ł")]


# font switches carry no text of their own; \it would otherwise leave "it"
FONT_CMDS = re.compile(r"\\(it|bf|em|tt|sc|rm|sf|sl|upshape|itshape|bfseries)\b\s*")
# \textbf{x}, \emph{x}: keep the argument, drop the command
TEXT_CMDS = re.compile(r"\\(textbf|textit|textrm|texttt|textsc|textsf|textsl|"
                       r"emph|underline|mbox|text)\s*(?=\{)")


def detex(s):
    """`Nikkil{\"a}` -> `Nikkilä`. Applies the accent instead of dropping it."""
    s = FONT_CMDS.sub("", s)
    for _ in range(4):                       # \textbf{\emph{x}} nests
        s, n = TEXT_CMDS.subn("", s)
        if not n:
            break
    def accent(m):
        mark = ACCENTS.get(m.group(1)) or BRACED_ACCENTS.get(m.group(1))
        return unicodedata.normalize("NFC", m.group(2) + mark) if mark else m.group(2)
    # \"{a} and \"a
    s = re.sub(r'\\(["\'`^~=.])\s*\{([A-Za-z])\}', accent, s)
    s = re.sub(r'\\(["\'`^~=.])\s*([A-Za-z])', accent, s)
    # \v{s}, \c{c}, ... only in the braced form, so \version is left alone
    s = re.sub(r"\\([vuHkrdb])\s*\{([A-Za-z])\}", accent, s)
    for tex, ch in LIGATURES:
        s = re.sub(re.escape(tex) + r"(?![A-Za-z])", ch, s)
    return s


def tidy(s):
    """Strip TeX braces and escapes, collapse whitespace."""
    if s is None:
        return None
    s = re.sub(r"\\&", "&", s)
    s = detex(s)
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
    """`Willem M.` -> `WM`"""
    out = []
    for chunk in re.split(r"[\s.-]+", given):
        if chunk:
            out.append(chunk[0].upper())
    return "".join(out)


def format_author(name):
    """`de Vos, Willem M.` / `Willem M. de Vos` -> `de Vos, W.M.`"""
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
    label = ("%s, %s" % (family, ini)).strip()
    return MARK % label if family.split()[-1] == ME else label


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
    """Where it appeared. A preprint says so, whichever server it is on."""
    name = e["journal"] or e["booktitle"] or e["series"] or e["school"] \
        or e["institution"] or e["publisher"] or e["howpublished"]
    if name and (e.get("pubstate") or "").strip().lower() == "preprint":
        if "preprint" not in name.lower():
            name += " preprint"
    return name


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
        out.append("URL: <%s>" % e["url"])
    return " ".join(out)


def unmarked(text):
    """Strip emphasis markup so punctuation can be checked underneath it."""
    return re.sub(r"\[|\]\{\.underline\}|\*", "", text)


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


def render(e, title_first):
    au, ti, ve, lo = author_list(e["author_raw"]), e["title"], venue(e), locator(e)

    # Remarks close every entry, whichever way round it is laid out.
    trailing = []
    if e["note"]:
        trailing.append("*%s*." % e["note"].rstrip("."))
    mark = authorship_note(e["authorship"])
    if mark:
        trailing.append("*%s*." % mark)
    if e.get("related_cites"):
        trailing.append("Associated publication: %s." % "; ".join(e["related_cites"]))

    if title_first:
        rest = [au if unmarked(au).endswith(".") else au + "."] if au else []
        if ve:
            rest.append("*%s.*" % ve + ((" " + lo + ".") if lo else ""))
        rest.append(tail(e))
        rest += trailing
        body = " ".join(x for x in rest if x)
        return "**%s**\n  %s" % (ti, body)

    parts = []
    if au:
        parts.append(au if unmarked(au).endswith(".") else au + ".")
    parts.append(ti.rstrip(".") + ".")
    if ve:
        parts.append("*%s*%s." % (ve, (" " + lo) if lo else ""))
    elif lo:
        parts.append(lo + ".")
    parts.append(tail(e))
    parts += trailing
    return " ".join(x for x in parts if x)


def sort_key(e):
    try:
        y = int(re.sub(r"\D", "", e["year"] or "0") or 0)
    except ValueError:
        y = 0
    mn = month_name(e["month"])
    return (-y, -(MONTHS.index(mn) + 1 if mn else 0), e["title"] or "")


# -------------------------------------------------------------------- output

def slug(text):
    """`Research data` -> `research-data`, for a preamble filename."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def preamble(cls):
    """Hand-written prose, if preambles/<cls>.md exists.

    A section takes its pubclass as the name; a subsection takes
    <pubclass>-<subtitle>, e.g. preambles/I2-research-data.md.
    """
    path = os.path.join(PREAMBLES, "%s.md" % cls)
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read().strip()
    return [text, ""] if text else []


def short_cite(e):
    """`Alneberg J et al. Nature Methods 2014. DOI:...` for a cross-reference."""
    names = split_authors(e["author_raw"])
    who = format_author(names[0]).replace("*", "") if names else ""
    if len(names) > 1:
        who += " et al."
    bits = [b for b in (who, venue(e), e["year"]) if b]
    out = " ".join(bits[:1]) + (" " + ", ".join(bits[1:]) if len(bits) > 1 else "")
    if e["doi"]:
        out += ". DOI:%s" % e["doi"]
    return out


def split_section(cls, entries):
    """[(subtitle, entries)] for a section, or one unlabelled block."""
    rules = SUBSECTIONS.get(cls)
    if not rules:
        return [(None, entries)]
    left, out = list(entries), []
    for cat, grp, subtitle in rules:
        take = [e for e in left
                if (cat is None or (e["entrysubtype"] or "") == cat)
                and (grp is None or (e["group"] or "") == grp)]
        if take:
            out.append((subtitle, take))
            left = [e for e in left if e not in take]
    if left:                       # nothing should fall through, but say so if it does
        out.append(("Other outputs", left))
    return out


def author_position(e):
    """(first, last) for LL on this entry, counting shared positions."""
    names = split_authors(e["author_raw"])
    if not names:
        return False, False
    def family(n):
        n = tidy(n)
        if n.startswith("{"):
            return ""
        if "," in n:
            return n.split(",")[0].strip()
        w = n.split()
        cut = len(w) - 1
        while cut > 0 and w[cut - 1][:1].islower():
            cut -= 1
        return " ".join(w[cut:])
    mine = [i for i, n in enumerate(names) if family(n).split()[-1:] == [ME]]
    if not mine:
        return False, False
    shared = "shared first" in (e["authorship"] or "").lower()
    return (mine[0] == 0 or shared), (mine[-1] == len(names) - 1)


def summary(entries, by_class):
    """A table of how many entries each section holds, and LL's position."""
    rows, tot = [], [0, 0, 0, 0]
    for cls, heading, _ in LAYOUT:
        group = by_class.get(cls) if cls else None
        if not group:
            continue
        first = sum(1 for e in group if author_position(e)[0])
        last = sum(1 for e in group if author_position(e)[1])
        shared = sum(1 for e in group
                     if "shared first" in (e["authorship"] or "").lower())
        rows.append((heading, len(group), first, last, shared))
        tot = [tot[0] + len(group), tot[1] + first, tot[2] + last, tot[3] + shared]
    out = ["**Summary**", "",
           "| Section | Entries | First author | Last author |",
           "|:---|---:|---:|---:|"]
    for heading, n, first, last, shared in rows:
        f = "%d" % first + (" (%d shared)" % shared if shared else "")
        out.append("| %s | %d | %s | %d |" % (heading, n, f, last))
    f = "%d" % tot[1] + (" (%d shared)" % tot[3] if tot[3] else "")
    out.append("| **Total** | **%d** | **%s** | **%d** |" % (tot[0], f, tot[2]))
    out += ["", "First and last author positions count shared first authorships,",
            "which are listed separately.", ""]
    return out


def build(entries, today):
    by_key = {e["key"]: e for e in entries}
    for e in entries:
        e["related_cites"] = []
        for ref in re.split(r"[,\s]+", e["related"] or ""):
            target = by_key.get(ref.strip())
            if target is not None:
                e["related_cites"].append(short_cite(target))
            elif ref.strip():
                sys.stderr.write("warning: %s has related = {%s}, which is not a "
                                 "key in this file\n" % (e["key"], ref.strip()))

    by_class = {}
    for e in entries:
        by_class.setdefault(e["pubclass"] or "?", []).append(e)

    def has_content(cls):
        """A section is worth printing if it has entries or hand-written prose."""
        return bool(by_class.get(cls)) or bool(preamble(cls))

    lines = ["#### List of publications", "",
             "Leo Lahti %s" % today.strftime("%-d.%-m.%Y"), ""]
    lines += summary(entries, by_class)
    for cls, heading, members in LAYOUT:
        if cls is None:
            if any(has_content(m) for m in members):
                lines += ["**%s**" % heading, ""]
            continue
        if not has_content(cls):
            continue
        lines += ["**%s**" % heading, ""]
        lines += preamble(cls)
        entries_here = sorted(by_class.get(cls, []), key=sort_key)
        bullet = cls in BULLETED
        for subtitle, block in split_section(cls, entries_here):
            if subtitle:
                lines += ["*%s*" % subtitle, ""]
                lines += preamble("%s-%s" % (cls, slug(subtitle)))
            for n, e in enumerate(block, 1):
                marker = "*" if bullet else "%d." % n
                lines += ["%s %s" % (marker, render(e, cls in TITLE_FIRST)), ""]

    unclassified = by_class.get("?", [])
    if unclassified:
        sys.stderr.write("warning: %d entries have no pubclass: %s\n"
                         % (len(unclassified),
                            ", ".join(e["key"] for e in unclassified)))
    return "\n".join(lines).rstrip() + "\n"


PDF_HEADER = os.path.join(HERE, "pdf-header.tex")
PDF_OPTS = [
    "--pdf-engine=xelatex",
    "--include-in-header=" + PDF_HEADER,
    "-V", "papersize=a4",
    "-V", "geometry:margin=2cm",
    "-V", "fontsize=10pt",
    "-V", "colorlinks=true",
    "-V", "linkcolor=blue",
    "-V", "urlcolor=blue",
    "-V", "mainfont=DejaVu Serif",
    "-V", "monofont=DejaVu Sans Mono",
]
# pandoc's built-in reference styles already give a clean Word document;
# drop a reference.docx next to this script to override them.
DOCX_OPTS = []
REFERENCE_DOCX = os.path.join(HERE, "reference.docx")


def render_file(md_text, out_path, opts):
    """Hand the markdown to pandoc and let it produce PDF or .docx."""
    if not shutil.which("pandoc"):
        sys.exit("error: pandoc is required to render %s" % out_path)
    if out_path.endswith(".docx") and os.path.exists(REFERENCE_DOCX):
        opts = opts + ["--reference-doc=" + REFERENCE_DOCX]
    tmp = out_path + ".md"
    open(tmp, "w", encoding="utf-8").write(md_text)
    try:
        proc = subprocess.run(["pandoc", tmp, "-o", out_path] + opts,
                              capture_output=True, text=True)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            sys.exit("error: pandoc failed to build %s" % out_path)
    finally:
        os.remove(tmp)
    sys.stderr.write("wrote %s\n" % out_path)


def derive(flag, output, suffix):
    """Work out where a rendered file goes."""
    if flag is not True:
        return flag
    if not output:
        sys.exit("error: --%s needs a path, or -o to derive one from" % suffix)
    return re.sub(r"\.md$", "", output) + "." + suffix


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-b", "--bib", default=BIB)
    ap.add_argument("-o", "--output", help="markdown output path")
    ap.add_argument("--pdf", nargs="?", const=True, default=None, metavar="PDF",
                    help="also render a PDF; defaults to OUTPUT with a .pdf "
                         "suffix when -o is given")
    ap.add_argument("--docx", nargs="?", const=True, default=None, metavar="DOCX",
                    help="also render a Word document; defaults to OUTPUT with "
                         "a .docx suffix when -o is given")
    args = ap.parse_args()

    text = build(parse(args.bib), date.today())
    if args.output:
        open(args.output, "w", encoding="utf-8").write(text)
        sys.stderr.write("wrote %s\n" % args.output)
    elif args.pdf is None and args.docx is None:
        sys.stdout.write(text)

    if args.pdf is not None:
        render_file(text, derive(args.pdf, args.output, "pdf"), PDF_OPTS)
    if args.docx is not None:
        render_file(text, derive(args.docx, args.output, "docx"), DOCX_OPTS)


if __name__ == "__main__":
    main()
