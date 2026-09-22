#!/usr/bin/env python3
"""One-time back-fill of the `pubclass` field into lahti.bib.

`pubclass` records the Finnish publication classification (A1, A2, A3, A5, B,
D, E1, G, I1, I2) plus the pre-publication states (preprint, submitted,
inpress) that structure the manual list of publications.  It is the one piece
of information the .bib did not already carry, and bib2publist.py needs it to
regenerate that list.

Classes were seeded by matching entries against the manually maintained
~/Seafile/Team/lahti_publ.md; the entries that could not be matched
automatically are listed in MANUAL below.  pandoc drops unknown fields, so
data/publications/lahti.json (and hence the website) is unaffected.
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(HERE, os.pardir, "lahti.bib")

# Entries with no counterpart in the manual list, or whose counterpart is
# prose rather than a citation; classified by hand.
MANUAL = {
    "Laitinen2018IDA":    "A5",  # listed under A5 #14 in the manual list
    "Sinkkonen03tr":      "B",   # listed under B #3
    "Lahti10thesis":      "G",   # doctoral thesis
    "Lahti03":            "G",   # M.Sc. thesis
    "Lahti09bsc":         "G",   # B.Sc. thesis
    "Lahti2002":          "G",   # special assignment in mathematics
    "Lahti2001":          "G",   # special assignment in mathematics
    "Lahti09rpa":         "I2",  # software
    "Lahti10dmt":         "I2",  # software
    "Lahti10netresponse": "I2",  # software
    "Lahti10pint":        "I2",  # software
    "Lahti11intcomp":     "I2",  # software
}


def main(mapping_path):
    with open(mapping_path) as fh:
        pubclass = json.load(fh)
    pubclass.update(MANUAL)

    raw = open(BIB, encoding="utf-8").read()
    out, i, added, skipped = [], 0, 0, 0
    pat = re.compile(r"@(\w+)\s*\{\s*([^,]+),", re.S)
    while True:
        m = pat.search(raw, i)
        if not m:
            break
        key = m.group(2).strip()
        # find the entry's closing brace
        j = raw.index("{", m.start())
        depth, k = 0, j
        while k < len(raw):
            if raw[k] == "{":
                depth += 1
            elif raw[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        body = raw[m.start():k + 1]

        out.append(raw[i:m.start()])
        if "pubclass" in body.lower() or key not in pubclass:
            if key not in pubclass:
                skipped += 1
            out.append(body)
        else:
            # match the indentation and alignment of the entry's first field
            fm = re.search(r"\n([ \t]*)(\w+)(\s*)=", body)
            indent = fm.group(1) if fm else "\t"
            pad = " " * max(1, len(fm.group(2)) + len(fm.group(3)) - len("pubclass")) if fm else " "
            line = "\n%spubclass%s= {%s}," % (indent, pad, pubclass[key])
            insert_at = body.index(",", body.index("{")) + 1
            out.append(body[:insert_at] + line + body[insert_at:])
            added += 1
        i = k + 1
    out.append(raw[i:])

    open(BIB, "w", encoding="utf-8").write("".join(out))
    print("pubclass added to %d entries; %d left untouched" % (added, skipped))


if __name__ == "__main__":
    main(sys.argv[1])
