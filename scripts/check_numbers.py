#!/usr/bin/env python3
import re, sys, argparse, collections, pathlib

REFS = [r"(?:附)?[表图式]\s*\d+(?:\.\d+)?", r"\d+(?:\.\d+)*\s*节", r"第\s*\d+\s*[章节条]", r"(?:Table|Fig\.|Figure|Eq\.|Section)\s*\d+[a-z]?",
        r"\[\d+(?:[,，\-–]\d+)*\]", r"^\s*\d+(?:\.\d+)*\s", r"\b4\.\d\b(?=\s*[一-鿿])"]

def nums(text, strip_refs):
    t = text.replace("−", "-").replace("–", "-").replace("，", ",")
    if strip_refs:
        for r in REFS: t = re.sub(r, " ", t, flags=re.M)
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    out = []
    for m in re.finditer(r"(?<![A-Za-z0-9.])-?\d+(?:\.\d+)?%?", t):
        s = m.group(0)
        pct = s.endswith("%"); s = s.rstrip("%")
        try: v = float(s)
        except ValueError: continue
        out.append(("%" if pct else "") + ("%g" % v))
    return collections.Counter(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original"); ap.add_argument("rewrite")
    ap.add_argument("--strip-refs", action="store_true"); ap.add_argument("--allow", nargs="*", default=[])
    a = ap.parse_args()
    o = nums(pathlib.Path(a.original).read_text(encoding="utf-8"), a.strip_refs)
    r = nums(pathlib.Path(a.rewrite).read_text(encoding="utf-8"), a.strip_refs)
    allow = {("%g" % float(x.rstrip("%"))) for x in a.allow}
    strip = lambda k: k.lstrip("%")
    miss = {k: v - r[k] for k, v in o.items() if r[k] < v and strip(k) not in allow}
    new = {k: v - o[k] for k, v in r.items() if o[k] < v and strip(k) not in allow}
    print(f"original: {sum(o.values())} numbers | rewrite: {sum(r.values())} numbers")
    if miss: print("MISSING in rewrite:", ", ".join(f"{k}(x{v})" for k, v in sorted(miss.items())))
    if new: print("NEW in rewrite:", ", ".join(f"{k}(x{v})" for k, v in sorted(new.items())))
    if not miss and not new: print("OK: every number preserved")
    sys.exit(1 if (miss or new) else 0)

if __name__ == "__main__":
    main()