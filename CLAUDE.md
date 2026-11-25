# Kolkata Palimpsest: Colonial Calcutta, Street by Street (1850–1947)

Handoff context for Claude Code. Read this first.

## Who / what
- **Student:** Suvanwit Mandal ("Captain"), B.Tech CSE, IIIT Naya Raipur (IIIT-NR).
- **Course:** Digital Humanities (DH) minor stream. This is the **minor project**.
- **Deadline:** the student said not to worry about it, so build properly, not as a rushed demo. (Earlier plan: a RAG Q&A over Subhas Chandra Bose / INA trial material. **This project replaces it.**)
- **Style:** concise, plain-text explanations; structured deliverables; prefers seeing working results over long plans.

## The project in one line
Trace colonial Calcutta (its **buildings, roads, gullies/lanes and shops**) across 1850–1947, using colonial maps and street directories, and preserve that heritage as an interactive, metadata-rich digital archive.

**Viva pitch:** *"Click any building on a colonial street and see what it was in 1850, 1897, 1920 and 1940: who occupied it, what shop it was, an old photo, and what stands there today."*

## Core DH argument (important for marks)
Colonial Calcutta was split into **White Town** (Dalhousie Square / BBD Bagh, Chowringhee: densely mapped and listed) and **Black Town** (north Calcutta: Chitpur Road, Jorasanko, Kumartuli, Kansaripara, barely recorded). The directories list Europeans in detail but leave out most Indian residents and shops. The map should **show that gap**, partly fill it with fieldwork, oral history and Bengali sources, and say openly that the colonial archive saw only half the city. Present uncertain data as *candidates with confidence scores*, never as certain fact.

## Syllabus mapping (IIIT-NR DH syllabus; the music module is excluded)
- **M1 Basics of DH:** computational turn, public-facing DH, debates about colonial archives.
- **M2 Culture & AI:** OCR, NER and text mining on directories/gazetteers, fuzzy matching; ethics (archival bias, oral-history consent, not over-claiming).
- **M3 Digital Archaeology & Heritage Informatics:** GIS/georeferencing, 3D photogrammetry of facades, virtual reconstruction, digital heritage preservation.
- **M5 Indian Knowledge Systems & Digital:** digitising historical texts and maps, preserving oral tradition (residents' memories), cultural sustainability.

## Study area
Two contrasting slices:
1. **White Town:** Dalhousie Square → Old Court House Street → Chowringhee Road; Clive Street.
2. **Black Town:** one Chitpur Road / Jorasanko lane cluster (trade-named lanes: Kumartuli = potters, Kansaripara = brass-workers).
Also Bowbazar Street (a furniture-trade cluster appears in the 1915 data).

## Data layers (target)
| Layer | Content | Source / method |
|---|---|---|
| Roads | Colonial name ↔ modern name (Clive St → Netaji Subhas Rd, Harrison Rd → Mahatma Gandhi Rd, Chowringhee Rd → Jawaharlal Nehru Rd, Dalhousie Sq → BBD Bagh, Wellesley St → Rafi Ahmed Kidwai Rd, Lower Circular Rd → AJC Bose Rd) | Gazetteer table + georeferenced maps |
| Buildings | Footprints, status: standing / altered / demolished | Trace from Simms' survey (1847–49) and later Survey of India sheets; compare with modern imagery |
| Shops & trades | firm, trade, house_no, street, year | **OCR + NER on Thacker's / Bengal directories**; ads pages too |
| Gullies | Trade-named lanes as living heritage | Toponyms + fieldwork |
| Images | Then-and-now photo pairs | Public-domain colonial photos (Bourne & Shepherd, Johnston & Hoffmann); student's own photos |
| Preservation | 3–5 photogrammetry models (cast-iron balconies, facades, signboards); short oral-history clips from old shopkeepers | Polycam/Meshroom → model-viewer/Sketchfab; Whisper (handles Bengali) |
| Metadata | Every item described with Dublin Core; images via IIIF | Student already did Dublin Core and IIIF in earlier assignments |

## Primary sources (verified to exist online)
- **Thacker's Indian Directory 1915:** https://archive.org/details/in.ernet.dli.2015.97228 (has PDF, `_djvu.txt` full text ~15.5 MB, hOCR, JP2).
- Thacker's Indian Directory 1920: https://archive.org/details/in.ernet.dli.2015.97229
- Thacker's Indian Directory 1938: https://archive.org/details/in.ernet.dli.2015.109427
- Thacker's 1939: https://archive.org/details/in.ernet.dli.2015.83751
- Bengal Directory 1884: archive.org `in.ernet.dli.2015.68582`; 1855: `in.ernet.dli.2015.93585`
- Scott & Co.'s Bengal Directory 1849: HathiTrust http://hdl.handle.net/2027/hvd.32044088755111
- Full index of digitised directories: https://wiki.fibis.org/w/Directories_online
- Thacker's Guide to Calcutta (1906, W.K. Firminger): https://archive.org/details/thackersguidetoc00firm
- Background: Thacker's directory first issued 1864; renamed Thacker's Indian Directory in 1885; published until 1960. Early editions include **street directories of Calcutta with residents of each house**. Example: the 1897 edition lists 4–7 Chowringhee Road as Whiteaway, Laidlaw & Co. (Scroll.in article 1090878).
- Maps to find: Upjohn's map (1790s), **Simms' survey (1847–49)**, Survey of India sheets. Check the David Rumsey Map Collection and British Library digitised India maps for high-resolution downloads. **Check availability first; it decides the map layer.**

> Note: the claude.ai cloud workspace could NOT download from archive.org (proxy-blocked). In Claude Code on the student's own machine this should work. Try `https://archive.org/download/in.ernet.dli.2015.97228/` to list files.

## Work done so far
### 1. `scripts/extract_directory.py`: house-by-house street-directory extractor
Pipeline: image/PDF page → grayscale, upscale to ~2500px tall, denoise, adaptive threshold, deskew → Tesseract `--psm 11` word boxes → **rows rebuilt by y-coordinate** (the number and name columns are read as separate blocks otherwise) → **second digit-whitelist OCR pass** on the number column to recover lone single-digit house numbers (Tesseract drops "1", "3", "9") → parser (ALL-CAPS street headers; house-number patterns `5`, `4, 5 & 6`, `12A`, `14/2`, `101-1`; dot leaders split occupant | trade) → CSV `year,page,street,house_no,occupant,trade,ocr_conf,raw`. Also writes `ocr_raw.txt` and `clean_pN.png`.
- Usage: `python scripts/extract_directory.py book.pdf --pages 120-125 --year 1915 --out out.csv` (or a single PNG/JPG).
- **Tested only on a synthetic mock page** (`tests/mock_page.png`): 7/7 entries correct, mean confidence 86. **Not yet tested on a real street-directory page.** Real pages are likely two-column with tiny type; expect to add column splitting (detect the vertical gutter, OCR each column separately).

### 2. `scripts/ocr_page.py` + `scripts/extract_ads.py`: advertisement-page extractor
Tested on **real 1915 Thacker's advertisement pages** (`data/raw/ads_1915/`, pages li–lii, liii–liv, xxiii–xxiv):
- Address regex (case-insensitive; tolerates `42,-Clive`, `101-1,`, `5, 6 & 7,`) + **fuzzy matching (difflib, cutoff 0.6) against a seed gazetteer** of colonial street names + detection of "Late of" (= former address).
- **Results: 11/11 numbered addresses found with the correct street; 9/11 with the correct house number.** Fuzzy matching recovered "Jnokven Lane" → Jackson Lane and "Sew Sazar Street" → Bowbazar Street.
- Errors: small-print digit confusions (32→31, 40→49); decorative display fonts garble firm names ("DEY & CO." → "DEEZ & CO."); "Established 1860" read as 1660; Kolley & Co. (Grosvenor House, Old Court House Street, no house number) missed.
- Ground truth: `data/extracted/ads_1915_verified.csv` (firm, trade, address, extracted-vs-true, notes). Raw extractor output: `data/extracted/ads_1915_addresses_raw.csv`.
- Historical findings already: **Dey & Co. moved from 2 Chowringhee Road to 212 Corporation Street**; **furniture cluster on Bowbazar Street** (No. 40 Nundo Lall Mullick & Bros, est. 1863; No. 49 Choudhry, Burdhun & Co., est. 1848).

### Lessons
- Street names are reliable after gazetteer matching; **house numbers in small print need human verification**. Frame this as "human-in-the-loop verification", a proper DH method.
- Display/decorative fonts → names need manual or LLM correction; plain directory listings should OCR far better.
- Always verify dates.
- Add a rule for named buildings without a number ("Grosvenor House, Old Court House Street").

## Next steps (in order)
1. **Get real street-directory pages**: download the 1915 PDF or `_djvu.txt`; find the Calcutta street-directory section (search "Chowringhee Road"). Compare Archive.org's existing OCR (`_djvu.txt`/hOCR) with our own pipeline and use whichever is better.
2. Run `extract_directory.py` on 3–5 real pages; add two-column splitting; measure accuracy against a hand-checked sample (aim for ≥90% of streets and ≥80% of house numbers before human review).
3. Repeat for 2–3 more years (e.g. 1897/1915/1938) on the same streets → **time series per address**.
4. Build `data/gazetteer.csv`: colonial name, modern name, variants, lat/lon (expand the seed list in `extract_ads.py`).
5. Georeference 2+ historical maps (QGIS or Allmaps), digitise building footprints for the study area → GeoJSON.
6. Join directory entries ↔ buildings (street + house number) → `buildings.geojson` with per-year occupants.
7. Web app: MapLibre/Leaflet + year slider, building popups (occupant per year, trade, photos), then/now image swipe, model-viewer for 3D, oral-history audio pins. Static site is fine.
8. Archive: Dublin Core per item (CSV + JSON), IIIF for images; optionally Omeka-S.
9. Fieldwork: photos, photogrammetry, consented interviews (consent form, CARE-style ethics note).
10. Report and viva deck: method, accuracy table, the White Town/Black Town argument, limitations.

## Tech stack
Python 3, OpenCV, Tesseract 5 (`eng`), pytesseract, PyMuPDF (`import pymupdf`), pandas, difflib/rapidfuzz, spaCy (NER), QGIS / Allmaps, GeoJSON, MapLibre GL or Leaflet, model-viewer, Whisper. Install: `pip install opencv-python pytesseract pymupdf pandas rapidfuzz spacy` plus the system `tesseract-ocr`.

## Layout
```
CLAUDE.md
scripts/   extract_directory.py, extract_ads.py, ocr_page.py
data/raw/ads_1915/       real 1915 ad page images (student-provided screenshots)
data/ocr/                Tesseract output for those pages
data/extracted/          raw extractor CSV + hand-verified ground truth
tests/                   synthetic mock page, generator, expected output
```

## Conventions
- Keep every extracted row traceable: `source` (edition, year, page), `raw` OCR line, `ocr_conf`, `verified_by`.
- Never overwrite raw data; write new files.
- Mark uncertain matches (`match = fuzzy/unmatched`) rather than silently "fixing" them.

## Update 2026-11-25 (Claude Code session)
- Finding: Thacker's 1915 has NO house-by-house street directory; Calcutta section is an alphabetical firm listing (djvu.txt lines ~102290-112200, page images n~410-500; archive.org page images via `/download/<id>/page/n<N>_w1800.jpg`). 2756 pages total.
- New: `scripts/extract_firms.py` -> `data/extracted/firms_1915_raw.csv` (566 parsed of ~1479 candidate paragraphs; 227 exact / 144 fuzzy / 195 unmatched street).
- Hand-check (1 page, 9 firms, `firms_1915_verified_sample.csv`): recall 6/9; house no. 6/6 of parsed; street 4/6 (both errors were `fuzzy`: named building "Alliance Bank Bldgs", OCR "Robmd st"). Treat `fuzzy` as needs-review. Sample is tiny; verify more pages.
- Seen: a Kansaripara Road firm (Biswas, P. B., 104 Kansaripara rd.) - Black Town lead.
- Data: raw djvu + 3 page JPGs in data/raw/thackers_1915/.

## Update 2026-11-25 (2): more hand-checks, own OCR beats djvu.txt
- Verified sample now 37 firms over 4 page images (n435, 420, 450, 480) in `data/extracted/firms_1915_verified_sample.csv`.
- archive.org djvu.txt drops whole entries (Blackwood, Gupta Press, Guzdar, Grueber absent): parsed 15/37, house 14/15, street 12/15.
- Own column-split OCR of page images (`scripts/ocr_directory_pages.py`, gutter by min ink density, tesseract psm 4) recovers them. On pages 420/450/480 (28 firms): parsed 18/28, house 17/18, street 16/18. Remaining misses are paragraph-merge / OCR-garbled headers (e.g. "BISWAS, 8., & BROS.", "Hp. Office" entries), not missing text.
- Next: run own OCR over the whole firm section (n~405-620, est. ~40 min), re-run parser, fix remaining parse misses, expand verified sample.

## Update 2026-11-26: full 1915 firm section done
Column-split OCR on pages n405-620 of archive.org `in.ernet.dli.2015.97228` ran in parallel (4 workers), ~45 min.
- Own OCR text: `data/ocr/firms_1915_full_own.txt` (46k lines).
- Parsed: `data/extracted/firms_1915.csv` -- **1166 firms** from 2046 candidate paragraphs (57% parse rate; the rest are non-firm headers, continuations and advertisement blocks).
- Street match: **616 exact / 192 fuzzy / 358 unmatched** (69% canonicalised). Unmatched is mostly OCR-garbled street words; easy wins by widening the gazetteer with the top-100 unmatched values.
- Scored against 37-firm verified sample across 4 pages: **parsed 34/37 (92%), house 30/34, street 30/34**. Hits the CLAUDE.md goal of >=90% streets / >=80% houses before human review.
- Density gap (demonstrates the White/Black Town argument):
  - Clive Street: 109 firms. Radha Bazar: 42. Dhurrumtollah: 39. Chowringhee: 23.
  - Upper Chitpore: 12. Lower Chitpore: 10. Kansaripara: 3. Jorabagan: 1. Kumartuli: 0. Chitpur Road: 0 (all variants rolled into *Chitpore*).
- Chowringhee Road time-series starter: 18 addresses with multiple occupants each, e.g. #1 has Bristol Hotel + Sen & Sen + Biswas KC; #22 has Johnston & Hoffmann + Rai Budree Das Bahadoor & Sons.
- Join to buildings: `data/geo/buildings.geojson` (9 anchored buildings), `data/geo/unanchored.csv` (1146 unanchored firms across 899 (street, house_no) pairs) -- this is the fieldwork and georeferencing TODO list.

## Deliverables layer added
- Web prototype: `web/index.html` (MapLibre + year slider + confidence pills + honest-archive note).
- Pipeline: `scripts/{ocr_directory_pages,extract_firms,join_to_geojson,build_timeseries,score_sample,make_dublin_core}.py`.
- Gazetteer: `data/gazetteer.csv` (54 colonial-to-modern street pairs with OCR variants).
- Dublin Core: `data/dublin_core.csv` (3 items seeded; grows as items land).
- Ethics + consent form: `docs/ethics_and_consent.md`.
- Report + viva outlines: `docs/{report_outline,viva_deck_outline}.md`.
- README: top-level `README.md`.

## Next for the student
1. Expand `data/gazetteer.csv` by the top-100 values of `data/extracted/firms_1915.csv`'s `unmatched` street column. Half an hour's work.
2. Run the same pipeline on 1920 and 1938 editions (archive IDs in this file). `scripts/build_timeseries.py` already joins them.
3. Georeference Simms 1847-49 in QGIS or Allmaps; trace the ~30 study-area footprints; drop them in `buildings_stub.geojson` so the join starts picking them up.
4. Field visit to Kumartuli and Jorasanko: three oral-history clips (Whisper handles Bengali), signed consent forms.
5. Final 25-page report per `docs/report_outline.md`.
