"""Fetch page images of a Thacker's volume from archive.org, split two columns, OCR each, write one text file.
Beats archive.org's own djvu.txt on the Calcutta firm listing (which drops whole entries).
Usage: python scripts/ocr_directory_pages.py --id in.ernet.dli.2015.97228 --first 420 --last 480 --out data/ocr/firms_1915_own.txt
Page images are cached in data/raw/<id>/pages/ (never overwritten). Raw text keeps a '#PAGE n col' marker per block.
"""
import argparse, os, subprocess, cv2, numpy as np, pytesseract

ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True); ap.add_argument("--first", type=int, required=True)
ap.add_argument("--last", type=int, required=True); ap.add_argument("--out", required=True)
ap.add_argument("--pages", help="comma list overriding first/last")
a = ap.parse_args()
d = f"data/raw/{a.id}/pages"; os.makedirs(d, exist_ok=True)
ns = [int(x) for x in a.pages.split(",")] if a.pages else range(a.first, a.last + 1)
with open(a.out, "w", encoding="utf-8") as out:
    for n in ns:
        p = f"{d}/n{n}.jpg"
        if not os.path.exists(p):
            subprocess.run(["curl", "-sL", "-m", "90", "-o", p,
                            f"https://archive.org/download/{a.id}/page/n{n}_w1800.jpg"], check=True)
        im = cv2.imread(p, 0)
        if im is None:
            continue
        h, w = im.shape
        b = np.convolve((im < 140).sum(0), np.ones(25) / 25, "same")
        lo, hi = int(w * .35), int(w * .65); g = lo + int(np.argmin(b[lo:hi]))
        for name, c in (("L", im[:, :g]), ("R", im[:, g:])):
            out.write(f"\n#PAGE {n} {name}\n" + pytesseract.image_to_string(c, config="--psm 4") + "\n")
        out.flush()
