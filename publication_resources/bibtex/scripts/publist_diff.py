#!/usr/bin/env python3
"""Report entries present in only one of lahti.bib / the manual list.

    python3 publist_diff.py [MANUAL_LIST.md]

Matches a manual-list item to a .bib entry by DOI first, then by overlap of
title words and author surnames.  Anything that fails to match is reported so
it can be added to whichever of the two lists is missing it.
"""
import argparse, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bib2publist import parse, tidy, LAYOUT, PREAMBLES  # noqa: E402

DEFAULT_MANUAL = os.path.expanduser("~/Seafile/Team/lahti_publ.md")
THRESHOLD = 0.62

SECTIONS = {h: c for c, h, _ in LAYOUT if c}
# headings in the manual list that differ from the generated ones
ALIASES = {
    "B Non‐refereed scientific articles": "B",
    "I2 ICT programs or applications": "I2",
    "Computer programs, talks, guest lectures, radio and television "
    "programmes etc.": "I2",
}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.replace("​", "").lower()).split())


STOP = set("a an the of and or in on for with to from by as at is are we our "
           "using use based via its it".split())


def toks(s):
    return set(w for w in norm(s).split() if w not in STOP and len(w) > 2)


def load_manual(path):
    text = open(path, encoding="utf-8").read().replace("​", "")
    section, items, cur = None, [], None
    for line in text.split("\n"):
        stripped = line.strip()
        head = re.match(r"^\*\*(.{2,90}?)\*\*$", stripped)
        if head:
            name = head.group(1).strip()
            cls = SECTIONS.get(name) or ALIASES.get(name)
            if cls or name.startswith(("A ", "E ", "I ", "G ")) or \
                    name in ("Preprints", "Submitted"):
                if cur:
                    items.append(cur)
                cur, section = None, cls
                continue
        li = re.match(r"^\s*(?:[0-9]+\.|\*|-)\s+(.*)$", line)
        if li and li.group(1).strip():
            if cur:
                items.append(cur)
            cur = {"section": section, "text": li.group(1).strip()}
        elif cur is not None and stripped:
            cur["text"] += " " + stripped
        elif cur is not None:
            items.append(cur)
            cur = None
        elif stripped and section:
            # plain paragraphs count too: the G section lists theses that way
            cur = {"section": section, "text": stripped}
    if cur:
        items.append(cur)
    return [i for i in items if len(i["text"]) > 30]


def preamble_tokens():
    """Words carried by the hand-written section preambles."""
    import glob
    out = set()
    for f in glob.glob(os.path.join(PREAMBLES, "*.md")):
        out |= toks(open(f, encoding="utf-8").read())
    return out


def doi_of(text):
    m = re.search(r"(10\.\d{4,9}/\S+)", text)
    if not m:
        return ""
    return re.sub(r"[\\`.,*\]\)]+$", "", m.group(1)).replace("\\_", "_").replace("\\", "").lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manual", nargs="?", default=DEFAULT_MANUAL)
    ap.add_argument("-b", "--bib",
                    default=os.path.join(HERE, os.pardir, "lahti.bib"))
    args = ap.parse_args()

    entries = parse(args.bib)
    for e in entries:
        e["ttoks"] = toks(e["title"])
        e["atoks"] = set(w for w in norm(e["author"]).split() if len(w) > 3)
        e["doi"] = (e["doi"] or "").lower().rstrip(".,")
    by_doi = {}
    for e in entries:
        if e["doi"]:
            by_doi.setdefault(e["doi"], e)

    items = load_manual(args.manual)
    for it in items:
        it["toks"] = toks(it["text"])
        it["doi"] = doi_of(it["text"])

    # Score every plausible pair, then assign one-to-one, best first, so that
    # two near-identical records cannot both claim the same .bib entry.
    candidates = []
    for ii, it in enumerate(items):
        hit = by_doi.get(it["doi"])
        if hit is not None:
            candidates.append((2.0, ii, hit["key"]))
            continue
        for e in entries:
            if not e["ttoks"]:
                continue
            cov = len(e["ttoks"] & it["toks"]) / len(e["ttoks"])
            acov = (len(e["atoks"] & it["toks"]) / len(e["atoks"])) if e["atoks"] else 0
            comb = 0.7 * cov + 0.3 * acov
            if comb >= THRESHOLD:
                candidates.append((comb, ii, e["key"]))
    candidates.sort(key=lambda c: -c[0])

    matched, taken_items, best_seen = set(), set(), {}
    for score, ii, key in candidates:
        best_seen[ii] = max(best_seen.get(ii, 0), score)
        if ii in taken_items or key in matched:
            continue
        taken_items.add(ii)
        matched.add(key)

    only_manual = []
    for ii, it in enumerate(items):
        if ii in taken_items:
            continue
        best, score = None, 0.0
        for e in entries:
            if not e["ttoks"]:
                continue
            cov = len(e["ttoks"] & it["toks"]) / len(e["ttoks"])
            acov = (len(e["atoks"] & it["toks"]) / len(e["atoks"])) if e["atoks"] else 0
            comb = 0.7 * cov + 0.3 * acov
            if comb > score:
                best, score = e, comb
        it["score"], it["near"] = score, best
        only_manual.append(it)

    only_bib = [e for e in entries if e["key"] not in matched]

    print("bib entries: %d   manual items: %d   matched: %d"
          % (len(entries), len(items), len(matched)))
    # Prose that the hand-written preambles already cover is not a gap.
    ptoks = preamble_tokens()
    covered = []
    for it in list(only_manual):
        if it["score"] < THRESHOLD and it["toks"] and \
                len(it["toks"] & ptoks) / len(it["toks"]) >= 0.7:
            only_manual.remove(it)
            covered.append(it)

    absent = [i for i in only_manual if i["score"] < THRESHOLD]
    dupes = [i for i in only_manual if i["score"] >= THRESHOLD]
    print("\n== in the manual list, not in lahti.bib (%d) ==" % len(absent))
    for it in sorted(absent, key=lambda x: (x["section"] or "~", -x["score"])):
        print("\n  [%s] closest: %s (%.2f)"
              % (it["section"], it["near"]["key"] if it["near"] else "-", it["score"]))
        print("    " + it["text"][:220])
    if dupes:
        print("\n== manual items whose .bib entry is already claimed by another "
              "item (%d) ==" % len(dupes))
        print("   (the manual list records these twice, or two records are near "
              "duplicates)")
        for it in sorted(dupes, key=lambda x: -x["score"]):
            print("\n  [%s] duplicate of: %s (%.2f)"
                  % (it["section"], it["near"]["key"] if it["near"] else "-", it["score"]))
            print("    " + it["text"][:200])
    if covered:
        print("\n== covered by a hand-written section preamble (%d) =="
              % len(covered))
        for it in covered:
            print("  [%s] %s" % (it["section"], it["text"][:110]))
    print("\n== in lahti.bib, not in the manual list (%d) ==" % len(only_bib))
    for e in sorted(only_bib, key=lambda x: x["year"] or ""):
        print("\n  %s [%s] %s" % (e["key"], e["pubclass"] or "no pubclass", e["year"] or ""))
        print("    " + (e["title"] or "")[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
