#!/usr/bin/env python3
"""把用户自己的 CSV / TSV / Excel-另存CSV / JSON 词表转换成背单词 app 的词库 JS。

用法：
    python3 tools/convert_csv_vocab.py mywords.csv --id mybank --label "我的词库 300 词"
        [--source 来源说明] [--out vocab/mybank.js] [--no-manifest]

列名认得这些（大小写、中英文都随意，缺的留空）：
    word/单词/vocabulary, phonetic/音标, pos/词性,
    def_en/英文释义/en, def_zh/中文释义/zh,
    example/例句, example_zh/例句翻译/例句译文,
    etymology/词根/词根词缀/记忆法, tags/标签, audio/音频

产出的 JS 会被 index.html 通过 vocab/manifest.js 自动加载；
也可以什么都不改，直接在 app 首页点「导入词库文件」选这个 JS。
"""
import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

ALIASES = {
    "word": ["word", "单词", "vocabulary", "vocab", "term"],
    "phonetic": ["phonetic", "phonetics", "ipa", "音标", "发音"],
    "pos": ["pos", "part_of_speech", "词性"],
    "def_en": ["def_en", "en", "english", "definition", "英文释义", "释义", "解释"],
    "def_zh": ["def_zh", "zh", "chinese", "中文释义", "中文", "翻译"],
    "example": ["example", "sentence", "例句"],
    "example_zh": ["example_zh", "example_cn", "例句翻译", "例句译文", "例句中文"],
    "etymology": ["etymology", "root", "memory", "词根", "词根词缀", "记忆法", "备注"],
    "tags": ["tags", "tag", "标签", "分类"],
    "audio": ["audio", "sound", "音频"],
}
CANON = {a: key for key, names in ALIASES.items() for a in names}


def read_rows(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        return data if isinstance(data, list) else data.get("words", [])
    delim = "\t" if path.suffix.lower() in (".tsv", ".txt") else ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    rows = [r for r in rows if any(str(c).strip() for c in r)]
    if not rows:
        return []
    head = [str(c).strip().lower() for c in rows[0]]
    if any(h in CANON for h in head):
        keys = [CANON.get(h) for h in head]
        out = []
        for r in rows[1:]:
            rec = {k: (r[i] if i < len(r) else "") for k, i in zip(keys, range(len(head))) if k}
            out.append(rec)
        return out
    # 没有表头：按 word, def_en, def_zh 的顺序硬吃
    return [{"word": r[0], "def_en": r[1] if len(r) > 1 else "", "def_zh": r[2] if len(r) > 2 else ""} for r in rows]


def norm_word(rec):
    def g(*names):
        for n in names:
            v = str(rec.get(n, "") or "").strip()
            if v:
                return re.sub(r"\s+", " ", v)
        return ""
    word = g("word", "单词", "vocabulary", "vocab", "term")
    if not word:
        return None
    tags = g("tags", "tag", "标签", "分类")
    return {
        "word": word,
        "phonetic": g("phonetic", "音标", "ipa") or "",
        "pos": g("pos", "词性") or "",
        "def_en": g("def_en", "en", "english", "definition", "英文释义", "释义", "解释"),
        "def_zh": g("def_zh", "zh", "chinese", "中文释义", "中文", "翻译"),
        "example": g("example", "例句", "sentence"),
        "example_zh": g("example_zh", "例句翻译", "例句译文", "例句中文"),
        "etymology": g("etymology", "词根", "词根词缀", "记忆法", "备注"),
        "tags": [t.strip() for t in re.split(r"[;,、|/]", tags) if t.strip()],
        "audio": g("audio", "音频") or "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_file")
    ap.add_argument("--id", required=False, default=None)
    ap.add_argument("--label", required=False, default=None)
    ap.add_argument("--source", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-manifest", action="store_true")
    args = ap.parse_args()

    src = Path(args.csv_file)
    if not src.exists():
        print(f"找不到文件：{src}", file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parent.parent          # vocab-app/
    bank_id = args.id or re.sub(r"[^a-z0-9]+", "_", src.stem.lower()).strip("_") or "mybank"
    words, skipped = [], 0
    for rec in read_rows(src):
        w = norm_word(rec)
        if not w or not (w["def_en"] or w["def_zh"]):
            skipped += 1
            continue
        words.append(w)
    if not words:
        print("没有解析出可用词条：至少要有 word + 一个释义列。", file=sys.stderr)
        return 1
    seen, unique = set(), []
    for w in words:
        k = w["word"].lower()
        if k in seen:
            skipped += 1
            continue
        seen.add(k)
        unique.append(w)

    out = (Path(args.out) if args.out else root / "vocab" / f"{bank_id}.js").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"id": bank_id, "label": args.label or f"{src.stem} · {len(unique)} 词",
                          "source": args.source or f"由 {src.name} 转换", "words": unique},
                         ensure_ascii=False, indent=1)
    out.write_text("// 由 tools/convert_csv_vocab.py 生成\nwindow.registerVocab(" + payload + ");\n",
                   encoding="utf-8")

    try:
        rel = out.relative_to(root).as_posix()
    except ValueError:
        rel = str(out)
    if not args.no_manifest:
        mf = root / "vocab" / "manifest.js"
        if mf.exists():
            text = mf.read_text(encoding="utf-8")
            if f'"{bank_id}"' not in text:
                label_js = json.dumps(args.label or src.stem, ensure_ascii=False)
                text = text.replace("];", f'  {{ id: "{bank_id}", label: {label_js}, file: "{rel}" }},\n];', 1)
                mf.write_text(text, encoding="utf-8")
                print(f"已登记进 {mf}")
            else:
                print(f"{mf} 里已有 id={bank_id}，未重复登记（如要更新 label 请手改）")
        else:
            mf.write_text("window.VOCAB_MANIFEST = [\n"
                          f'  {{ id: "{bank_id}", label: "{src.stem}", file: "{rel}" }},\n];\n', encoding="utf-8")
    print(f"词库 {out} —— {len(unique)} 词（跳过 {skipped} 行：缺字段或重复）")
    print("下一步：双击 vocab-app/index.html，首页就能看到它。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
