"""Join firm CSVs to the buildings stub by (street, house_no) and emit buildings.geojson.

Fuzzy-matched streets get their canonical form via data/gazetteer.csv's variants column.
Output: data/geo/buildings.geojson (per feature: occupants={year:[{firm,trade,match}]}).
Any firm with no building anchor is logged to data/geo/unanchored.csv so you see which
(street, house_no) pairs want a coordinate before the full map lands.
"""
import argparse, json, csv, pandas as pd, re

ap = argparse.ArgumentParser()
ap.add_argument("firms_csvs", nargs="+")
ap.add_argument("--stub", default="data/geo/buildings_stub.geojson")
ap.add_argument("--gaz", default="data/gazetteer.csv")
ap.add_argument("--out", default="data/geo/buildings.geojson")
ap.add_argument("--unanchored", default="data/geo/unanchored.csv")
a = ap.parse_args()

stub = json.load(open(a.stub))
anchors = {(f["properties"]["street"], str(f["properties"]["house_no"])): f for f in stub["features"]}
gaz = pd.read_csv(a.gaz)
variant_map = {}
for _, r in gaz.iterrows():
    variant_map[r.colonial_name.lower()] = r.colonial_name
    for v in str(r.get("variants") or "").split("|"):
        v = v.strip()
        if v:
            variant_map[v.lower()] = r.colonial_name


def canon(s):
    return variant_map.get(str(s).lower(), s)


un = []
for p in a.firms_csvs:
    d = pd.read_csv(p)
    y = int(re.search(r"(\d{4})", p).group(1))
    for _, r in d.iterrows():
        s = canon(r.street); h = str(r.house_no).strip()
        feat = anchors.get((s, h))
        if not feat:
            un.append(dict(year=y, street=s, house_no=h, firm=r.firm, trade=r.trade, match=r.match)); continue
        occ = feat["properties"].setdefault("occupants", {})
        if isinstance(occ, str):
            occ = json.loads(occ); feat["properties"]["occupants"] = occ
        occ.setdefault(str(y), []).append(dict(firm=r.firm, trade=r.trade, match=r.match))

json.dump(stub, open(a.out, "w"), indent=1)
with open(a.unanchored, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["year", "street", "house_no", "firm", "trade", "match"])
    w.writeheader(); w.writerows(un)
print(f"wrote {a.out} ({len(stub['features'])} buildings) and {a.unanchored} ({len(un)} unanchored firms)")
