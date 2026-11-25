"""
Calcutta street-directory extractor (Thacker's-style pages).

Usage:
    python extract_directory.py <page.png|page.jpg|book.pdf> [--pages 120-125] [--year 1915] [--out out.csv]

Pipeline: image -> clean-up (grayscale, upscale, denoise, binarise, deskew)
          -> Tesseract OCR -> line parser -> CSV of (year, street, house_no, occupant, trade, raw, conf)
"""
import argparse, csv, re, sys
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

# ---------- 1. image clean-up ----------
def preprocess(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    h = gray.shape[0]
    if h < 2500:                                   # small type: upscale before OCR
        f = 2500 / h
        gray = cv2.resize(gray, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    gray = cv2.fastNlMeansDenoising(gray, h=15)
    bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 41, 15)
    # deskew using the angle of the ink pixels
    coords = np.column_stack(np.where(bw < 128))
    if len(coords) > 100:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        if 45 < abs(angle):
            angle = 0
        if abs(angle) > 0.2:
            M = cv2.getRotationMatrix2D((bw.shape[1] / 2, bw.shape[0] / 2), angle, 1.0)
            bw = cv2.warpAffine(bw, M, (bw.shape[1], bw.shape[0]),
                                flags=cv2.INTER_CUBIC, borderValue=255)
    return bw

# ---------- 2. OCR (line text + mean word confidence) ----------
def ocr_lines(bw: np.ndarray):
    """Rebuild printed rows from word boxes, so a house-number column and a
    name column that Tesseract reads as separate blocks are re-joined by height."""
    d = pytesseract.image_to_data(bw, lang="eng", config="--psm 11",
                                  output_type=pytesseract.Output.DICT)
    words = [(d["top"][i] + d["height"][i] / 2, d["left"][i], d["text"][i],
              float(d["conf"][i]), d["height"][i])
             for i in range(len(d["text"])) if d["text"][i].strip()]
    if not words:
        return
    med_h = float(np.median([w[4] for w in words]))
    rows = []
    for w in sorted(words):                       # sort by vertical centre
        if rows and abs(w[0] - rows[-1]["y"]) < 0.6 * med_h:
            r = rows[-1]; r["w"].append(w)
            r["y"] = sum(x[0] for x in r["w"]) / len(r["w"])
        else:
            rows.append({"y": w[0], "w": [w]})
    # x where the name column starts = most common left edge of non-numeric first words
    firsts = [min(r["w"], key=lambda x: x[1]) for r in rows]
    name_x = [f[1] for f in firsts if not re.match(r"^\d", f[2])]
    col_x = float(np.median(name_x)) if name_x else 0
    for r in rows:
        ws = sorted(r["w"], key=lambda x: x[1])   # left -> right
        text = " ".join(x[2] for x in ws)
        conf = round(sum(x[3] for x in ws) / len(ws), 1)
        # second pass: a row starting at the name column has probably lost a
        # short house number - re-OCR the strip to its left with a digit whitelist
        if col_x > 0 and abs(ws[0][1] - col_x) < med_h and not text.isupper():
            y0 = int(r["y"] - med_h); y1 = int(r["y"] + med_h)
            strip = bw[max(0, y0):y1, 0:max(1, int(col_x - med_h * 0.3))]
            if strip.size and (strip < 128).sum() > 20:
                pad = cv2.copyMakeBorder(strip, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
                num = pytesseract.image_to_string(
                    pad, config="--psm 7 -c tessedit_char_whitelist=0123456789/-&,AB").strip()
                if re.match(r"^\d", num):
                    text = f"{num} {text}"
        yield text, conf

# ---------- 3. parse directory lines ----------
STREET_RE = re.compile(
    r"^[A-Z][A-Z .'&-]{2,}(ROAD|STREET|LANE|SQUARE|PLACE|ROW|GHAT|BAZAR|BAZAAR|GULLY|GALLI|SARANI|AVENUE|CHOWRINGHEE)\.?$")
# house numbers: "5", "4, 5, 6 & 7", "12-1", "23/2", "15A"
HOUSE_RE = re.compile(r"^((?:\d+[A-Za-z]?(?:[/-]\d+)?)(?:\s*(?:,|&|and|to)\s*\d+[A-Za-z]?(?:[/-]\d+)?)*)[.,]?\s+(.+)$")
LEADER_RE = re.compile(r"\s*[.…·]{2,}\s*")   # dot leaders "......"

def clean(s: str) -> str:
    s = LEADER_RE.sub(" | ", s)
    s = s.replace("—", "-").replace("–", "-")
    return re.sub(r"\s{2,}", " ", s).strip(" |")

def parse(lines, year):
    street = None
    for raw, conf in lines:
        txt = clean(raw)
        if not txt:
            continue
        if STREET_RE.match(txt.upper()) and txt.upper() == txt:
            street = txt.rstrip(".").title()
            continue
        m = HOUSE_RE.match(txt)
        if m and street:
            house, rest = m.group(1), m.group(2)
            parts = [p.strip() for p in re.split(r"\s*\|\s*", rest) if p.strip()]
            if len(parts) == 1:                      # "Name, trade"
                occ, _, trade = parts[0].partition(", ")
                # keep "& Co." style names intact: only split trade if it's lower-case
                if trade and trade[:1].isupper():
                    occ, trade = parts[0], ""
            else:
                occ, trade = parts[0], ", ".join(parts[1:])
            yield {"year": year, "street": street, "house_no": house,
                   "occupant": occ.strip(" ,."), "trade": trade.strip(" ,."),
                   "raw": raw, "ocr_conf": conf}

# ---------- driver ----------
def load_images(path: Path, pages):
    if path.suffix.lower() == ".pdf":
        import pymupdf
        doc = pymupdf.open(path)
        rng = range(len(doc)) if not pages else range(pages[0] - 1, pages[1])
        for p in rng:
            pix = doc[p].get_pixmap(dpi=300)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)
            yield p + 1, cv2.cvtColor(img, cv2.COLOR_RGB2BGR if pix.n == 3 else cv2.COLOR_RGBA2BGR)
    else:
        yield 1, cv2.imread(str(path))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--pages", help="e.g. 120-125 (PDF only)")
    ap.add_argument("--year", default="")
    ap.add_argument("--out", default="directory_extract.csv")
    a = ap.parse_args()
    pages = tuple(map(int, a.pages.split("-"))) if a.pages else None

    rows, all_lines = [], []
    for pno, img in load_images(Path(a.src), pages):
        bw = preprocess(img)
        cv2.imwrite(f"clean_p{pno}.png", bw)
        lines = list(ocr_lines(bw))
        all_lines += [f"[p{pno} conf={c}] {t}" for t, c in lines]
        for r in parse(lines, a.year):
            r["page"] = pno
            rows.append(r)

    Path("ocr_raw.txt").write_text("\n".join(all_lines), encoding="utf-8")
    fields = ["year", "page", "street", "house_no", "occupant", "trade", "ocr_conf", "raw"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    confs = [r["ocr_conf"] for r in rows]
    print(f"lines OCR'd: {len(all_lines)} | entries parsed: {len(rows)} | "
          f"mean conf: {sum(confs)/len(confs) if confs else 0:.1f} -> {a.out}")

if __name__ == "__main__":
    main()
