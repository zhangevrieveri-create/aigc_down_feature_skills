#!/usr/bin/env python3
import json, sys, datetime, statistics

def verdict(c, r, tol): return "ok" if abs(c - r) <= tol else "FLAG"

def run(check):
    t, tol = check["type"], check.get("tol")
    rows, out, notes = check["rows"], [], []
    if t == "ratio":
        tol = tol or 0.003
        for r in rows:
            c = r["num"] / r["den"]; out.append((r["label"], round(c, 4), r["reported"], verdict(c, r["reported"], tol)))
        offs = [(r["label"], round(r["num"] - r["reported"] * r["den"], 4)) for r, o in zip(rows, out) if o[3] == "FLAG"]
        if len(offs) >= 3:
            vals = [x[1] for x in offs]
            if max(vals) - min(vals) <= 0.0015 + 0.1 * abs(statistics.mean(vals)):
                notes.append(f"CONSTANT OFFSET: numerator exceeds reported*denominator by ~{statistics.mean(vals):.4f} in every flagged row {offs}. Ask for the program output.")
        for r, o in zip(rows, out):
            if o[1] * r["reported"] < 0: notes.append(f"SIGN MISMATCH in {r['label']}: computed {o[1]} vs reported {r['reported']}")
    elif t == "calmar":
        tol = tol or 0.005
        for r in rows:
            c = r["annual"] / abs(r["mdd"]); out.append((r["label"], round(c, 3), r["reported"], verdict(c, r["reported"], tol)))
            if out[-1][3] == "FLAG": notes.append(f"{r['label']}: reported Calmar implies max drawdown {r['annual']/r['reported']:.2f} (table says {abs(r['mdd'])})")
    elif t == "annualize":
        tol = tol or 0.15
        if "years" in check: yrs = check["years"]
        else:
            d = (datetime.date.fromisoformat(check["end"]) - datetime.date.fromisoformat(check["start"])).days
            yrs = d / check.get("basis", 365)
        import math
        implied = []
        for r in rows:
            c = ((1 + r["total"] / 100) ** (1 / yrs) - 1) * 100
            out.append((r["label"], round(c, 2), r["reported"], verdict(c, r["reported"], tol)))
            implied.append((r["label"], round(math.log(1 + r["total"] / 100) / math.log(1 + r["reported"] / 100), 2)))
        notes.append(f"horizon used: {yrs:.3f} years; implied horizon per row: {implied}")
        ys = [y for _, y in implied]
        if max(ys) - min(ys) > 0.1: notes.append("INCONSISTENT HORIZONS: rows over the same window imply different lengths.")
    elif t == "pct":
        tol = tol or 0.15
        for r in rows:
            c = (r["a"] / r["b"] - 1) * 100 if check["mode"] == "higher" else (r["b"] - r["a"]) / r["b"] * 100
            out.append((r["label"], round(c, 2), r["reported"], verdict(c, r["reported"], tol)))
    elif t == "identity":
        tol = tol or 0.011
        for r in rows:
            ts = r["terms"]; c = sum(ts) if check["op"] == "sum" else ts[0] - sum(ts[1:])
            out.append((r["label"], round(c, 4), r["reported"], verdict(c, r["reported"], tol)))
    else:
        raise SystemExit(f"unknown check type {t}")
    return out, notes

def main():
    if len(sys.argv) < 2:
        print("Usage: python audit_metrics.py spec.json"); sys.exit(1)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    bad = 0
    for i, ch in enumerate(spec["checks"], 1):
        out, notes = run(ch)
        print(f"\n[{i}] {ch['type']} {ch.get('name','')}")
        print(f"{'row':<28}{'computed':>12}{'reported':>12}  verdict")
        for lab, c, r, v in out:
            print(f"{lab:<28}{c:>12}{r:>12}  {v}"); bad += v == "FLAG"
        for n in notes: print("  >>", n)
    print(f"\n{bad} flagged row(s)")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()