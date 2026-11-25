"""Join firm CSVs from multiple years into a per-address time series.

Usage: python scripts/build_timeseries.py data/extracted/firms_1915.csv data/extracted/firms_1920.csv --out data/extracted/addresses_timeseries.csv

Output: street, house_no, year, firm, trade, match (one row per firm-year), plus addresses.csv
with one row per (street, house_no) and columns firms_<year> listing occupants that year.
"""
import argparse, pandas as pd, re, os

ap = argparse.ArgumentParser()
ap.add_argument("csvs", nargs="+")
ap.add_argument("--out", required=True)
a = ap.parse_args()

dfs = []
for p in a.csvs:
    d = pd.read_csv(p)
    if "year" not in d or d.year.isna().all():
        d["year"] = int(re.search(r"(\d{4})", os.path.basename(p)).group(1))
    dfs.append(d[["year", "firm", "house_no", "street", "match", "trade"]])
df = pd.concat(dfs, ignore_index=True)
df["house_no"] = df.house_no.astype(str).str.strip()
df.to_csv(a.out, index=False)

piv = (df.groupby(["street", "house_no", "year"])["firm"]
         .apply(lambda s: " | ".join(sorted(set(s)))).unstack("year"))
piv.columns = [f"firms_{c}" for c in piv.columns]
piv.reset_index().to_csv(a.out.replace(".csv", "_pivot.csv"), index=False)
print(f"wrote {a.out} ({len(df)} rows) and {a.out.replace('.csv','_pivot.csv')} ({len(piv)} addresses)")
