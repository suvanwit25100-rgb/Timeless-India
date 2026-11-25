"""Pull (house_no, street) addresses out of OCR'd advertisement pages."""
import re, sys, csv
SUFFIX = r"(Street|Lane|Road|Square|Place|Row|Ghat|Bazar|Gully|Galli)"
# tolerate OCR noise: '42,-Clive', '101-1, Clive', 'Lall Bazar Street', '5, 6 & 7, Madan Gopal Lane'
ADDR = re.compile(r"(\d+(?:-\d+)?(?:\s*,\s*\d+)*(?:\s*&\s*\d+)?)[\s,.\-]+((?:[A-Z][A-Za-z]+\s+){1,3})" + SUFFIX, re.I)
import difflib
# seed gazetteer of colonial street names (extend from maps/directories as the project grows)
GAZ = ["Clive Street","Lall Bazar Street","Madan Gopal Lane","Jackson Lane","Corporation Street",
       "Chowringhee Road","Jorabagan Street","Bowbazar Street","Old Court House Street","Park Street",
       "Dharamtala Street","Chitpur Road","Harrison Road","College Street","Wellesley Street"]
def norm(st):
    st = st.title().replace("Bow Bazar","Bowbazar")
    best = difflib.get_close_matches(st, GAZ, n=1, cutoff=0.6)
    return (best[0], "exact" if best and best[0]==st else ("fuzzy" if best else "unmatched")) if best else (st,"unmatched")
rows = []
for fn in sys.argv[1:]:
    lines = open(fn).read().splitlines()
    for i, ln in enumerate(lines):
        for m in ADDR.finditer(ln):
            street = (m.group(2) + m.group(3)).strip()
            street, match = norm(street)
            past = bool(re.search(r"\b[LlSs]?ate of\b", ln[:m.start()]))
            rows.append({"page_img": fn, "house_no": re.sub(r"\s+", "", m.group(1)),
                         "street": street, "match": match, "status": "former" if past else "current",
                         "context": ln.strip()[:70]})
w = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
