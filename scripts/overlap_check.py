#!/usr/bin/env python3
import argparse, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from style_extract import read_text, detect_lang, split_sentences, shingles

ROOT = pathlib.Path(__file__).resolve().parent.parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rewrite"); ap.add_argument("--style", action="append", default=[])
    ap.add_argument("--ref", nargs="*", default=[]); ap.add_argument("--flag", type=float, default=0.35)
    a = ap.parse_args()
    text = pathlib.Path(a.rewrite).read_text(encoding="utf-8"); lang = detect_lang(text)
    corpus = set(); used = []
    for s in a.style:
        p = ROOT / "styles" / s / "fingerprints.json"
        if p.exists(): corpus |= set(json.loads(p.read_text())); used.append(s)
        else: print(f"[note] style {s} has no fingerprints")
    for r in a.ref: corpus |= shingles(read_text(r), lang); used.append(r)
    if not corpus: sys.exit("no reference fingerprints available")
    flagged, tot, hit = [], 0, 0
    for s in split_sentences(text, lang):
        sh = shingles(s, lang)
        if not sh: continue
        h = len(sh & corpus); tot += len(sh); hit += h
        if h / len(sh) >= a.flag: flagged.append((h / len(sh), s))
    print(f"compared against: {', '.join(used)}")
    print(f"overall shingle overlap: {hit}/{tot} = {hit / max(tot, 1):.1%}")
    if flagged:
        print(f"{len(flagged)} sentence(s) too close to the corpus - rewrite them:")
        for r, s in sorted(flagged, reverse=True): print(f"  [{r:.0%}] {s}")
        sys.exit(1)
    print("OK: no sentence is close to the corpus")

if __name__ == "__main__":
    main()