# Kolkata Palimpsest

Colonial Calcutta, street by street - 1850 to 1947. Digital Humanities minor project at IIIT Naya Raipur.

**Pitch**: *Click any building on a colonial street and see what it was in 1850, 1897, 1920 and 1940: who occupied it, what shop it was, an old photo, and what stands there today.*

See [CLAUDE.md](CLAUDE.md) for the full brief and session notes, and [docs/report_outline.md](docs/report_outline.md) for the report plan.

## Run the web prototype

```bash
python3 -m http.server --bind 127.0.0.1 8765
```

Then open http://127.0.0.1:8765/web/ and click a pin. The year slider shows the nearest listed year; the confidence pill tells you whether the street match was exact, fuzzy or unmatched.

## What's in the repo

| path | what |
|---|---|
| `scripts/extract_firms.py` | Parse the Calcutta firm listing from Thacker's text or own OCR. |
| `scripts/ocr_directory_pages.py` | Fetch page images from archive.org, split two columns, OCR each. |
| `scripts/extract_directory.py` | House-by-house street-directory parser (for editions that have one, e.g. 1897). |
| `scripts/extract_ads.py`, `scripts/ocr_page.py` | Ad-page extractor used on the 1915 ads. |
| `scripts/join_to_geojson.py` | Join firm CSVs into `data/geo/buildings.geojson`. |
| `scripts/build_timeseries.py` | Join multiple years into a per-address time series. |
| `scripts/make_dublin_core.py` | Dublin Core metadata CSV for every item. |
| `scripts/score_sample.py` | Score a parsed CSV against a hand-verified sample. |
| `data/gazetteer.csv` | Colonial-to-modern street names with OCR variants and White/Black Town tag. |
| `data/geo/buildings_stub.geojson` | Nine hand-placed anchor points for UI prototyping. |
| `data/extracted/firms_1915_verified_sample.csv` | Hand-checked ground truth for parser accuracy. |
| `docs/ethics_and_consent.md` | Oral-history consent form; CARE note. |
| `docs/report_outline.md`, `docs/viva_deck_outline.md` | Report and viva plans. |
| `web/index.html`, `web/README.md` | The MapLibre viewer. |

## Current status (2026-11-25)

- Thacker's 1915 downloaded (16 MB text + 216 page images 405-620).
- Firm parser tested on three real pages: 92% paragraphs parsed, 22/26 right on house, 22/26 right on street.
- Full-section OCR + parse in progress.
- Nine-building stub map works end-to-end with year slider and confidence pills.

Next: finish OCR, full parse, pull 1920 and 1938, georeference Simms 1847-49, trace footprints, drop the real `buildings.geojson` in.
