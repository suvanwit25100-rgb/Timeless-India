"""Parse the Calcutta alphabetical firm listing from Thacker's (own OCR or archive.org *_djvu.txt).

Paragraph shape: FIRM NAME[, optional named building], house_no, Street suffix, trade. Propr.- ...
Output CSV: year,line,firm,house_no,street_raw,street,match,trade,ocr_flag,raw
Never overwrites input; uncertain street matches are marked fuzzy/unmatched, not fixed.

Strategy: match ANY (house, street-words, street-suffix) occurrence inside the first 200 chars
of the paragraph, then take the firm as everything before it. This handles both
"FIRM, 31, Harrison rd." and "FIRM, Alliance Bank Bldgs., 8-1, Corporation st.".

Usage: python scripts/extract_firms.py in.txt --year 1915 --out out.csv  [--start N --end N]
"""
import re, csv, argparse, difflib

GAZ = [
    "Clive Street", "Clive Row", "Lall Bazar Street", "Lall Bazar", "Madan Gopal Lane",
    "Jackson Lane", "Corporation Street", "Chowringhee Road", "Chowringhee Place",
    "Jorabagan Street", "Bowbazar Street", "Old Court House Street", "Park Street",
    "Dharamtala Street", "Dhurrumtollah Street", "Chitpur Road", "Upper Chitpore Road",
    "Lower Chitpore Road", "Harrison Road", "College Street", "Wellesley Street",
    "Wellesley Place", "Wellington Street", "Strand Road", "Canning Street",
    "Amherst Street", "Hastings Street", "Mission Row", "Old China Bazar Street",
    "Royal Exchange Place", "Royal Exchange", "Dalhousie Square", "Lyons Range",
    "Mangoe Lane", "Bentinck Street", "Free School Street", "Mott's Lane",
    "Radha Bazar Street", "Radha Bazar", "Swallow Lane", "Cross Street", "Lindsay Street",
    "Upper Circular Road", "Lower Circular Road", "Bonfield Lane", "Fairlie Place",
    "Cornwallis Street", "Canal Street", "Prinsep Street", "Sheriff Lane",
    "Ezra Street", "Robert Street", "Royd Street", "Sukea Lane", "Fenchurch Street",
    "Kansaripara Road", "Kansareepara Road", "Hare Street", "Esplanade", "Cotton Street",
    "Armenian Street", "Amratolla Street", "Pollock Street", "Amherst Street",
    "Padma Nath Lane", "Okhil Mistry Lane", "Water Lane", "Garden Reach", "Colootolla Street",
]
GAZ = sorted(set(GAZ))

# Street-suffix tokens tolerant of common OCR slips
SUFFIX = (r"(?:st|at|it|sé|sl|si|s!|sq|sg|rd|rf|ri|rrf|rrd|ln|pl|pi|place|lane|square|"
          r"road|street|row|range|bazar|ghat|chowringhee|esplanade|reach|court|circus)")
# ABBR normalises the OCR'd suffix back to canonical form
ABBR = {
    "at": "Street", "it": "Street", "si": "Street", "sé": "Street", "sl": "Street",
    "s!": "Street", "sq": "Square", "sg": "Square", "rf": "Road", "ri": "Road",
    "rrf": "Road", "rrd": "Road", "st": "Street", "rd": "Road", "pl": "Place",
    "pi": "Place", "ln": "Lane",
}

ADDR = re.compile(
    r"(?P<house>\d{1,3}[A-Za-z]?(?:\s*[-,&]\s*\d{1,3}[A-Za-z]?)*)[,.\]]?\s+"
    r"(?P<street>(?:[A-Za-z'’]+\s+){0,3}?[A-Za-z'’]+)\s+(?P<suf>" + SUFFIX + r")\b\.?",
    re.I,
)


def norm_street(s_words, suffix):
    s = re.sub(r"\s+", " ", s_words).strip(" .,")
    suf = ABBR.get(suffix.lower().rstrip("."), suffix.title())
    # stop at trailing noise words
    s = re.sub(r"\b(ordered|the|only|and|&)$", "", s, flags=re.I).strip()
    full = f"{s} {suf}".title().strip()
    full = (full.replace("Bow Bazar", "Bowbazar")
                .replace("Lull Bazar", "Lall Bazar")
                .replace("Oliva", "Clive")
                .replace("Clire", "Clive")
                .replace("Cormwallis", "Cornwallis")
                .replace("Ohowringhee", "Chowringhee")
                .replace("Caotrringhee", "Chowringhee"))
    if full in GAZ:
        return full, "exact"
    m = difflib.get_close_matches(full, GAZ, n=1, cutoff=0.78)
    return (m[0], "fuzzy") if m else (full, "unmatched")


# mid-paragraph fresh firm start: >=4 upper-case, then ", <initials>, <digit>"
FIRM_START = re.compile(r"\b([A-Z][A-Z]{3,}(?:\s+[A-Z][A-Z]+)?,\s+(?:[A-Z]\.?\s*,?\s*){0,4}\d{1,4})")


def split_firms(para):
    """Split a merged paragraph at mid-string ALL-CAPS firm starts (e.g. two listings glued by OCR)."""
    hits = [m.start() for m in FIRM_START.finditer(para)]
    if len(hits) < 2:
        return [para]
    out, prev = [], 0
    for h in hits[1:]:
        if h - prev > 30:
            out.append(para[prev:h].strip()); prev = h
    out.append(para[prev:].strip())
    return [p for p in out if p]


def paragraphs(lines, start, end):
    buf, first = [], start
    for i in range(start, min(end, len(lines))):
        ln = lines[i].strip()
        if ln.startswith("#PAGE"):
            if buf:
                for p in split_firms(" ".join(buf)):
                    yield first, p
                buf = []
            continue
        if ln:
            if not buf:
                first = i + 1
            buf.append(ln)
        elif buf:
            for p in split_firms(" ".join(buf)):
                yield first, p
            buf = []
    if buf:
        for p in split_firms(" ".join(buf)):
            yield first, p


def parse(para):
    """Return (firm, house, street_raw, street, match, trade) or None."""
    m = ADDR.search(para[:220])
    if not m:
        return None
    firm = para[:m.start()].strip(" ,.;")
    # firm must start with a capital and be mostly uppercase
    if not re.match(r"^[A-Z\"“][A-Z0-9 .,&'\-\"“”]{2,}", firm):
        return None
    street, match = norm_street(m["street"], m["suf"])
    rest = para[m.end():]
    trade = re.split(r"\b(?:Propr|Ptnrs?|Mang|Manr|Mano|Phone|Tel|Code|Asst|Hd\.|Office|PROPR|MANGR)",
                     rest, 1, flags=re.I)[0]
    trade = trade.strip(" .,;")[:90]
    return firm, re.sub(r"\s+", "", m["house"]), m.group("street") + " " + m.group("suf"), street, match, trade


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("txt"); ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=10**9); ap.add_argument("--year", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lines = open(a.txt, encoding="utf-8", errors="replace").read().splitlines()
    rows, cand = [], 0
    for ln_no, para in paragraphs(lines, a.start, a.end):
        para = re.sub(r"\s+", " ", para)
        if not re.match(r"^[A-Z\"“][A-Z0-9 .,&'\-\"“”]{2,}[,.]", para):
            continue
        cand += 1
        p = parse(para)
        if not p:
            continue
        firm, house, sraw, street, match, trade = p
        rows.append(dict(year=a.year, line=ln_no, firm=firm, house_no=house,
                         street_raw=sraw.strip(), street=street, match=match, trade=trade,
                         ocr_flag="check" if re.search(r"[^\x00-\x7f]", firm) else "",
                         raw=para[:160]))
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    ex = sum(r["match"] == "exact" for r in rows); fz = sum(r["match"] == "fuzzy" for r in rows)
    print(f"candidate entries {cand}; parsed {len(rows)}; "
          f"street exact {ex}, fuzzy {fz}, unmatched {len(rows)-ex-fz}")


if __name__ == "__main__":
    main()
