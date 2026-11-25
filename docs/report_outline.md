# Kolkata Palimpsest - minor-project report outline

Target length: 25-30 pages. Audience: DH minor-stream evaluators. Argument-first: method and tables support the argument, not the other way round.

## 0. Abstract (1 page)

One paragraph: what the project does, what the archive hides, what the map shows.

## 1. Argument (2 pages)

Colonial Calcutta's directories saw White Town densely and Black Town barely. A map that pretends otherwise reproduces the gap. This project traces the gap, partly fills it, and shows its own confidence openly.

## 2. Literature / background (2 pages)

- Public-facing DH and the computational turn (M1).
- Recent work on colonial-archive bias: cite one or two papers via the Consensus search once connected.
- Prior Calcutta digitisation: FIBIS, archive.org's Thacker's holdings, Scroll.in's Chowringhee piece.

## 3. Sources (2 pages)

Table: Thacker's 1915 (archive.org `in.ernet.dli.2015.97228`), 1920, 1938; Bengal Directory 1884, 1855; Scott & Co. 1849; Thacker's Guide 1906; maps (Upjohn 1790s, Simms 1847-49, Survey of India). Say explicitly which were downloadable for this run.

## 4. Method (6 pages)

### 4.1 Text layer
1. Download `_djvu.txt` and page images via archive.org's `/page/n<N>_w1800.jpg`.
2. Column-split by minimum ink density; Tesseract psm 4 on each column (see `scripts/ocr_directory_pages.py`). Explain why this beat archive.org's own text (it dropped Blackwood, Gupta Press, Guzdar, Grueber).
3. Firm parser (`scripts/extract_firms.py`): paragraph splitter on mid-paragraph ALL-CAPS firm starts; address regex tolerant of OCR slips (`sé`, `rrf`); street normaliser against a 54-entry gazetteer.
4. Human-in-the-loop verification: `firms_1915_verified_sample.csv`. Numbers go in Table 1.

### 4.2 Map layer
1. Gazetteer (`data/gazetteer.csv`) ties each colonial name to a modern one and OCR variants; White/Black Town tag.
2. Building footprints: georeference Simms 1847-49 in QGIS, trace study-area polygons, save as GeoJSON.
3. Join directory rows to buildings via `scripts/join_to_geojson.py`; emit `buildings.geojson`.

### 4.3 Preservation layer
Photogrammetry (Polycam) on 3-5 facades; model-viewer in the map. Oral-history clips (Whisper transcription) pinned to buildings.

### 4.4 Metadata layer
Dublin Core for every item (`scripts/make_dublin_core.py`); IIIF manifests for images.

## 5. Study area walks (4 pages)

- Chowringhee: Bristol Hotel at #1, Johnston & Hoffmann at #22, Whiteaway at #4-7 in 1897.
- Clive Street: Martin & Co. at #6-7 (Sir Rajendra Nath Mookerjee, the first Indian partner in a major British firm).
- Bowbazar Street: 1915 furniture cluster (Nundo Lall Mullick at #40 est. 1863, Choudhry Burdhun at #49 est. 1848). This is a Black Town trade cluster the colonial listing *does* show.
- Kansaripara Road #104: Biswas P.B., plater and engraver - one of the few Black Town addresses the 1915 listing records.
- Dey & Co. moved from 2 Chowringhee Road to 212 Corporation Street - a tiny biography told by the 1915 ad pages.

## 6. Accuracy (2 pages)

Table 1: parse / house / street accuracy across hand-verified pages. Source text (archive.org djvu vs own column OCR). Known failure modes (digit confusions, decorative fonts, paragraph merges).

## 7. The web app (2 pages)

Screenshots of the map at 1897, 1915, 1920, 1940. Describe the confidence pill, the honest-archive note, the year slider.

## 8. Limitations and ethics (2 pages)

- What the archive misses and how the map shows it.
- CARE-style consent and withdrawal; translator present.
- Three things the project did NOT do (listed plainly).

## 9. Future work (1 page)

Omeka-S deposit; Bengali-source NER; crowdsourced Black Town corrections via a comment pin.

## 10. Appendices

A. Full `firms_1915_raw.csv` (printed at small type).
B. Full gazetteer.
C. Hand-verified ground-truth table.
D. Consent form.
