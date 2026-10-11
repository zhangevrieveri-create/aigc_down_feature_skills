#!/usr/bin/env python3
import argparse, json, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from style_extract import read_text, detect_lang

ROOT = pathlib.Path(__file__).resolve().parent.parent

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()
    text = read_text(a.file); lang = detect_lang(text); low = text.lower()
    reg = json.loads((ROOT / "styles" / "_registry.json").read_text(encoding="utf-8"))["styles"]
    scored = []
    for s in reg:
        if s["language"] != lang: continue
        hits = {k: low.count(k.lower()) for k in s.get("keywords", [])}
        score = sum(math.log1p(v) for v in hits.values())
        scored.append((score, s, {k: v for k, v in hits.items() if v}))
    scored.sort(key=lambda x: -x[0])
    print(f"manuscript language: {lang}")
    if not scored: print("no registered style for this language -> ingest a corpus"); return
    for sc, s, h in scored[:a.top]:
        print(f"{s['id']:<16} score={sc:5.2f} status={s['status']:<18} n_docs={s.get('n_docs',0)} hits={h}")
    top = scored[0]; second = scored[1][0] if len(scored) > 1 else 0
    conf = (top[0] - second) / (top[0] + 1)
    verdict = "confident" if top[0] >= 3 and conf >= 0.25 else "NOT confident - confirm with the user"
    if top[1]["status"] not in ("trained", "seeded", "seeded-few-samples"):
        verdict += f"; style status is '{top[1]['status']}' (prior only) - offer to ingest samples"
    print(f"suggestion: {top[1]['id']} ({verdict})")

if __name__ == "__main__":
    main()