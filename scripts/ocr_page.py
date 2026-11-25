"""OCR a full-page image (ads / free text). Usage: python ocr_page.py page.png [out.txt]"""
import sys, cv2, pytesseract
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + ".txt"
im = cv2.imread(src, 0)
im = cv2.resize(im, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
_, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
open(out, "w").write(pytesseract.image_to_string(bw, config="--psm 3"))
print("wrote", out)
