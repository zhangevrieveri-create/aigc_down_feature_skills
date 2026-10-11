#!/usr/bin/env python3
import re, sys, json, argparse, collections, statistics, pathlib, zlib, html, subprocess

ZH_CONN = ["首先","其次","再次","最后","此外","同时","另外","因此","所以","因而","从而","由于","考虑到","为了","为避免","为进一步","为检验","为验证","为考察",
           "具体来说","具体而言","换言之","相比之下","相反","然而","但是","不过","虽然","尽管","一方面","另一方面","进一步","同样","类似地","此处","其中",
           "可知","可以看出","表明","说明","证明","体现","验证","符合","一致","因篇幅所限","需要说明","值得注意","综上","总之","上述","前文","下文","本节","本文",
           "而","则","仍","也","均","分别","尤其","特别是","例如","如","即","以及","并且","在此基础上"]
EN_CONN = ["however","moreover","furthermore","in addition","therefore","thus","hence","consequently","notably","importantly","in contrast","by contrast",
           "similarly","here we","we show","we find","we observe","we demonstrate","our results","these results","suggest","consistent with","in particular",
           "for example","specifically","first","second","third","finally","overall","taken together","whereas","although","while","rather than","indeed","together","note that","hence","intuitively","as a result","in what follows","it is worth","to appreciate","naturally","to this end","to address","in summary","recall that","we leave","to the best of our knowledge","it is noteworthy","namely","for instance","similar to","compared with","on the other hand","next","otherwise","meanwhile","besides","additionally","accordingly","as shown","as a matter of fact","in short","that is"]
ZH_PRON = {"其":r"其(?![中次他实余间一])","该":"该","我们":"我们","本文":"本文","本节":"本节","笔者":"笔者","这":"这"}
EN_PRON = {"we":r"\bwe\b","our":r"\bour\b","it":r"\bit\b","this":r"\bthis\b","these":r"\bthese\b","they":r"\bthey\b"}
ZH_HEDGE = ["可能","较为","一定程度","有所","大致","基本","或许","略","相对"]
EN_HEDGE = ["may","might","could","suggest","appear","likely","potentially","indicate","seem"]

def read_text(path):
    p = pathlib.Path(path); suf = p.suffix.lower()
    if suf in (".txt", ".md", ""): return p.read_text(encoding="utf-8", errors="ignore")
    if suf == ".pdf":
        try:
            raw = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True, check=True).stdout
            return clean_academic_text(raw)
        except Exception as e:
            raise SystemExit(f"pdftotext failed for {p}: {e}")
    if suf == ".docx":
        import zipfile
        with zipfile.ZipFile(p) as z: xml = z.read("word/document.xml").decode("utf8", "ignore")
        xml = re.sub(r"</w:p>", "\n", xml)
        return html.unescape(re.sub(r"<[^>]+>", "", xml))
    raise SystemExit(f"unsupported file type: {p}")

def clean_academic_text(t):
    m = list(re.finditer(r"\n\s*(?:References|REFERENCES|Bibliography)\s*\n", t))
    if m: t = t[:m[-1].start()]
    t = re.sub(r"-\n(?=[a-z])", "", t)
    keep = []
    for ln in t.split("\n"):
        s = ln.strip()
        if not s: keep.append(""); continue
        if sum(c.isalpha() for c in s) / len(s) < 0.55: continue
        if len(s.split()) < 4 and not s.endswith((".", ":", ";", ",")): continue
        keep.append(s)
    t = "\n".join(keep)
    return re.sub(r"(?<![.!?:\n])\n(?!\n)", " ", t)

def detect_lang(text):
    t = re.sub(r"\s", "", text)
    if not t: return "en"
    cjk = len(re.findall(r"[\u4e00-\u9fff]", t))
    return "zh" if cjk / len(t) > 0.3 else "en"

def split_sentences(text, lang):
    text = re.sub(r"[ \t]+", " ", text)
    if lang == "zh": parts = re.split(r"(?<=[。！？!?])", re.sub(r"\n+", "", text))
    else: parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\[(])", re.sub(r"\s*\n\s*", " ", text))     return [p.strip() for p in parts if len(p.strip()) >= (6 if lang == "zh" else 20)]  def _units(s, lang): return len(re.sub(r"\s", "", s)) if lang == "zh" else len(s.split())  def norm_for_shingle(text, lang):     if lang == "zh":         t = re.sub(r"\s+", "", text)         t = re.sub(r"[，。；：、！？“”‘’（）()\[\]【】《》\-—…·,.;:!?\"'*]", "", t)
        return re.sub(r"\d+(?:\.\d+)?", "#", t)
    return re.sub(r"[^a-z0-9# ]", "", re.sub(r"\d+(?:\.\d+)?", "#", text.lower()))

def shingles(text, lang, n=None):
    t = norm_for_shingle(text, lang)
    if lang == "zh":
        n = n or 10
        return {zlib.crc32(t[i:i+n].encode()) for i in range(max(0, len(t)-n+1))}
    n = n or 7; w = t.split()
    return {zlib.crc32(" ".join(w[i:i+n]).encode()) for i in range(max(0, len(w)-n+1))}

def features(text):
    lang = detect_lang(text); sents = split_sentences(text, lang)
    lens = [_units(s, lang) for s in sents] or [0]; n_units = sum(lens)
    per1k = lambda c: round(c * 1000 / max(n_units, 1), 2)
    f = {"lang": lang, "n_sentences": len(sents), "n_units": n_units}
    q = statistics.quantiles(lens, n=4) if len(lens) >= 4 else [lens[0]] * 3
    f["sentence_len"] = {"mean": round(statistics.mean(lens), 1), "p25": q[0], "median": q[1], "p75": q[2], "max": max(lens)}
    f["commas_per_sentence"] = round(sum(len(re.findall(r"[，,]", s)) for s in sents) / max(len(sents), 1), 2)
    f["semicolons_per_100_sentences"] = round(100 * sum(len(re.findall(r"[；;]", s)) for s in sents) / max(len(sents), 1), 1)
    f["numbers_per_sentence"] = round(sum(len(re.findall(r"\d+(?:\.\d+)?", s)) for s in sents) / max(len(sents), 1), 2)
    body = "\n".join(sents); low = body.lower()
    if lang == "zh":
        conn = {c: body.count(c) for c in ZH_CONN}
        pron = {k: len(re.findall(v, body)) for k, v in ZH_PRON.items()}
        hedge = {h: body.count(h) for h in ZH_HEDGE}
        strip = lambda s: re.sub(r"^[\s\d\.\(\)（）一二三四五六七八九十、，]+", "", s)
        o2 = collections.Counter(strip(s)[:2] for s in sents)
        o4 = collections.Counter(strip(s)[:4] for s in sents)
        refs = collections.Counter(re.sub(r"\d+", "#", m) for m in re.findall(r"[由根据从参见见][图表式]\s*\d+[^，。；（）]{0,6}|[图表]\s*\d+(?:展示|给出|列出|报告|显示|描述)了?|（见[图表]\s*\d+）|[图表]\s*\d+所示", body))
        cite = len(re.findall(r"（[^（）]{1,40}?，\s*\d{4}[a-z]?）|\[\d+(?:[,，\-–]\d+)*\]|文\s*\[\d+\]", body))
    else:
        conn = {c: len(re.findall(r"\b" + re.escape(c) + r"\b", low)) for c in EN_CONN}
        pron = {k: len(re.findall(v, low)) for k, v in EN_PRON.items()}
        hedge = {h: len(re.findall(r"\b" + h + r"\w*", low)) for h in EN_HEDGE}
        o2 = collections.Counter(" ".join(s.lower().split()[:1]) for s in sents)
        o4 = collections.Counter(" ".join(s.lower().split()[:3]) for s in sents)
        refs = collections.Counter(re.sub(r"\d+", "#", m) for m in re.findall(r"(?:Fig\.|Figure|Figs\.|Table|Extended Data Fig\.)\s*\d+[a-z]?", body))
        cite = len(re.findall(r"\[\d+(?:[,–-]\d+)*\]|\([A-Z][A-Za-z\-]+(?:,? (?:andert{}&) [A-Z][A-Za-z\-]+ert{} et al\.?)?,? \d{4}[a-z]?\)|[A-Z][A-Za-z\-]+(?: (?:and|&) [A-Z][A-Za-z\-]+| et al\.?)? \(\d{4}[a-z]?\)", body))
    f["connectives_per_1000"] = dict(sorted(((k, per1k(v)) for k, v in conn.items() if v), key=lambda x: -x[1])[:30])
    f["pronoun_per_1000"] = {k: per1k(v) for k, v in pron.items()}
    f["hedging_per_1000"] = {k: per1k(v) for k, v in hedge.items() if v}
    f["sentence_openers_short"] = o2.most_common(12)
    f["sentence_openers_long"] = [x for x in o4.most_common(12) if x[1] > 1]
    f["figure_table_reference_templates"] = refs.most_common(12)
    f["citations_per_1000"] = per1k(cite)
    paras = [p for p in re.split(r"\n\s*\n|\n", text) if len(p.strip()) >= 30]
    f["n_paragraphs"] = len(paras); f["sentences_per_paragraph"] = round(len(sents) / max(len(paras), 1), 1)
    return f

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("files", nargs="+"); ap.add_argument("--out")
    a = ap.parse_args(); text = "\n\n".join(read_text(p) for p in a.files)
    feats = features(text); feats["n_docs"] = len(a.files)
    s = json.dumps(feats, ensure_ascii=False, indent=2)
    if a.out: pathlib.Path(a.out).write_text(s, encoding="utf-8")
    print(s)

if __name__ == "__main__":
    main()