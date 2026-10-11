#!/usr/bin/env python3
import argparse, json, pathlib, hashlib, datetime, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from style_extract import read_text, features, detect_lang, shingles

ROOT = pathlib.Path(__file__).resolve().parent.parent
STYLES = ROOT / "styles"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True); ap.add_argument("--name", required=True)
    ap.add_argument("--lang", choices=["zh", "en", "auto"], default="auto")
    ap.add_argument("--keywords", default="", help="comma separated field keywords")
    ap.add_argument("--keep-corpus", action="store_true"); ap.add_argument("--append", action="store_true")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()
    sd = STYLES / a.id; sd.mkdir(parents=True, exist_ok=True)
    texts, names = [], []
    for f in a.files:
        t = read_text(f); texts.append(t); names.append(pathlib.Path(f).name)
    if not texts: sys.exit("no input files")
    big = "\n\n".join(texts)
    lang = detect_lang(big) if a.lang == "auto" else a.lang
    feats = features(big); feats["n_docs"] = len(texts)
    feats["sources"] = [{"file": n, "sha1": hashlib.sha1(t.encode()).hexdigest()[:10]} for n, t in zip(names, texts)]
    (sd / "features.json").write_text(json.dumps(feats, ensure_ascii=False, indent=2), encoding="utf-8")
    fp = set()
    for t in texts: fp |= shingles(t, lang)
    (sd / "fingerprints.json").write_text(json.dumps(sorted(fp)), encoding="utf-8")
    prof = sd / "profile.md"
    if not prof.exists():
        tpl = (STYLES / "_template" / "profile.md").read_text(encoding="utf-8")
        prof.write_text(tpl.replace("{{ID}}", a.id).replace("{{NAME}}", a.name).replace("{{LANG}}", lang), encoding="utf-8")
    regp = STYLES / "_registry.json"
    reg = json.loads(regp.read_text(encoding="utf-8")) if regp.exists() else {"styles": []}
    reg["styles"] = [s for s in reg["styles"] if s["id"] != a.id]
    reg["styles"].append({"id": a.id, "name": a.name, "language": lang,
        "status": "trained" if len(texts) >= 3 else "seeded-few-samples", "n_docs": len(texts),
        "keywords": [k.strip() for k in a.keywords.split(",") if k.strip()],
        "updated": datetime.date.today().isoformat(), "profile": f"styles/{a.id}/profile.md"})
    regp.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ingested {len(texts)} doc(s) -> styles/{a.id}/ (lang={lang})")

if __name__ == "__main__":
    main()