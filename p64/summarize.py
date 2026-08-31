"""Build the certificate table from results/*.json."""
import glob
import json

rows = {"cubic": [], "bip": []}
for f in glob.glob("results/*_n*.json"):
    d = json.load(open(f))
    rows["bip" if d.get("bipartite") else "cubic"].append(d)

for k in rows:
    rows[k].sort(key=lambda d: d["n"])

for k, name in [("cubic", "ALL CONNECTED CUBIC GRAPHS"),
                ("bip", "CONNECTED CUBIC BIPARTITE GRAPHS")]:
    R = rows[k]
    if not R:
        continue
    ns = [d["n"] for d in R]
    gaps = [n for n in range(4, max(ns) + 1, 2) if n not in ns]
    tot = sum(d["tree_nodes"] for d in R)
    ce = sum(len(d["counterexamples"]) for d in R)
    print(f"\n### {name}")
    print(f"| n | forbidden lengths | search-tree nodes | survivors | counterexamples | wall |")
    print("|---|---|---|---|---|---|")
    for d in R:
        print(f"| {d['n']} | {d['all_pow2_lengths']} | {d['tree_nodes']:,} | "
              f"{d['survivors_C4C8C16']} | {len(d['counterexamples'])} | "
              f"{d['wall_secs']:.1f}s |")
    print(f"\ncovered even n: {min(ns)}..{max(ns)}   MISSING: {gaps if gaps else 'none'}")
    print(f"total tree nodes: {tot:,}   total counterexamples found: {ce}")
    if not gaps and ce == 0:
        print(f"==> CERTIFIED: no {name.lower()} counterexample on <= {max(ns)} vertices.")
