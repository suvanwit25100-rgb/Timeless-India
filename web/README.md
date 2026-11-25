# Kolkata Palimpsest - web prototype

A static viewer over the vintage Kolkata map image (assets/kolkata-map.webp), with pins placed by a two-point lat/lon calibration in map.html, with a year slider (1850-1947). Click any pin to see the firms listed at that address in the nearest listed year.

Current data: 9 hand-placed anchor points in `data/geo/buildings_stub.geojson`, drawn from the 1915 Thacker's parse and one 1897 reference (Whiteaway, Laidlaw at 4-7 Chowringhee Road, from the Scroll.in article). Markers are coloured by White Town / Black Town / shared.

Run locally:

```bash
python3 -m http.server --directory . 8000
```

then open http://localhost:8000/web/

## Replace the stub when real data lands

1. Georeference Simms' 1847-49 Calcutta survey or a Survey of India sheet in QGIS (or Allmaps). Export building footprints inside the study area as a polygon GeoJSON.
2. Join each polygon to directory rows on `(street, house_no)` using `data/gazetteer.csv` for colonial-name matching.
3. Embed the per-year occupant list in each feature's `properties.occupants` as `{year: [{firm, trade, match, source}]}`.
4. Drop that file in `data/geo/buildings.geojson` and update the `fetch(...)` path in `index.html`.

## Notes shown to the viewer

The sidebar states openly that the colonial archive mostly recorded European firms, that fuzzy/unmatched rows are candidates not certain facts, and lists the source edition. Keep that panel honest as data grows.
