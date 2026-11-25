"""Emit a Dublin Core CSV describing each project item (directories, maps, photos, 3D models, oral-history clips).

Columns follow DCMI Terms: title, creator, subject, description, publisher, contributor,
date, type, format, identifier, source, language, relation, coverage, rights.

Reads an input manifest (data/items.csv) with free-form columns and writes dublin_core.csv.
Call it once before the final report so every archive item has a Dublin Core record.
"""
import csv, os, pandas as pd

DC = ["title","creator","subject","description","publisher","contributor","date","type",
      "format","identifier","source","language","relation","coverage","rights"]

INPUT = "data/items.csv"
OUT = "data/dublin_core.csv"

if not os.path.exists(INPUT):
    # seed with a few known items
    seed = [
        dict(title="Thacker's Indian Directory 1915", creator="Thacker, Spink & Co.",
             subject="Calcutta; business directory; colonial India", date="1915",
             type="Text", format="PDF; plain text; JPEG scans", identifier="in.ernet.dli.2015.97228",
             source="https://archive.org/details/in.ernet.dli.2015.97228",
             language="en", coverage="Calcutta, 1915", rights="Public domain",
             description="Alphabetical merchants/firms listing; ad pages for Calcutta businesses."),
        dict(title="Buildings stub for colonial Calcutta", creator="Kolkata Palimpsest project",
             subject="Calcutta; buildings; GIS; heritage", date="2026",
             type="Dataset", format="GeoJSON", identifier="data/geo/buildings_stub.geojson",
             language="en", coverage="Calcutta, 1850-1947", rights="CC-BY 4.0",
             description="Hand-placed anchor points for UI prototyping; to be replaced by footprints traced off Simms 1847-49."),
        dict(title="Street gazetteer, colonial<->modern", creator="Kolkata Palimpsest project",
             subject="Calcutta; toponymy; street names", date="2026",
             type="Dataset", format="CSV", identifier="data/gazetteer.csv",
             language="en", coverage="Calcutta, 1850-1947", rights="CC-BY 4.0",
             description="Colonial to modern street name mapping; OCR variants and White/Black Town tags."),
    ]
    pd.DataFrame(seed).to_csv(INPUT, index=False)
    print(f"seeded {INPUT} with 3 items")

df = pd.read_csv(INPUT)
for c in DC:
    if c not in df: df[c] = ""
df[DC].to_csv(OUT, index=False)
print(f"wrote {OUT} ({len(df)} items)")
