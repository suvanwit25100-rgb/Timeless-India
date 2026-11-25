"""Score a parsed firms CSV against a hand-verified sample CSV.

Match by: first 5 alpha chars of firm name AND house number equal, else by firm similarity.
Prints per-row verdicts and overall counts.
"""
import sys, re, pandas as pd, difflib

parsed_csv, verified_csv = sys.argv[1], sys.argv[2]
d = pd.read_csv(parsed_csv); v = pd.read_csv(verified_csv)
if "page_image_n" in v.columns and len(sys.argv) > 3:
    v = v[v.page_image_n.isin([int(x) for x in sys.argv[3].split(",")])]

alpha = lambda s: re.sub(r"[^A-Z]", "", str(s).upper())
d["k"] = d.firm.map(alpha)
v["k"] = v.firm.map(alpha)

P = H = S = 0; misses = []
for _, r in v.iterrows():
    cand = d[d.k.str.startswith(r.k[:5])] if r.k else d.iloc[0:0]
    best = cand[cand.house_no.astype(str).str.replace(r"\D","",regex=True)==str(r.true_house).replace("-","")]
    if len(best): x = best.iloc[0]
    elif len(cand):
        names = cand.firm.tolist()
        m = difflib.get_close_matches(r.firm, names, n=1, cutoff=0.5)
        x = cand[cand.firm == m[0]].iloc[0] if m else cand.iloc[0]
    else:
        misses.append(r.firm); continue
    P += 1
    h_ok = str(x.house_no).replace("-","") == str(r.true_house).replace("-","")
    s_ok = x.street == r.true_street
    H += h_ok; S += s_ok
    if not (h_ok and s_ok):
        print(f"WRONG {r.firm:30s} | {r.true_house:5s} {r.true_street:25s} -> {x.house_no!s:5s} {x.street!s:25s} ({x.match})")

print(f"MISS ({len(misses)}): " + ", ".join(misses[:20]))
print(f"total {len(v)}  parsed {P}  house {H}/{P}  street {S}/{P}  "
      f"overall parse {P}/{len(v)} ({100*P//max(1,len(v))}%)")
