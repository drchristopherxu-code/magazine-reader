# 背单词 · Vocabulary Trainer

纯前端单文件应用：双击 `index.html` 即可使用，不依赖 Node、不联网、没有外部 CDN。
学习进度与错题本存在浏览器 `localStorage`（本机在 Chromium 内核浏览器里验证通过，
Chrome / Edge / Safari 都可以；用无痕窗口则关掉窗口后进度不保留）。

## 目录

```
vocab-app/
  index.html                     ← 双击这个
  vocab/manifest.js              ← 词库清单（在这里登记新词库）
  vocab/eco_2026_10_31.js        ← 经济学人 2026-10-31 期生词库（自动生成，443 词 · en-GB）
  vocab/ny_2026_11_02.js         ← 纽约客 2026-11-02 期生词库（自动生成，454 词 · en-US）
  tools/convert_csv_vocab.py     ← CSV / TSV / JSON → 词库 JS
  tools/sample_words.csv         ← 词表格式示例
```

整个文件夹要放在一起，别只拷 `index.html`（词库在 `vocab/` 里）。

## 五种页面

| 页面 | 干什么 |
|---|---|
| 首页 | 选词库；🎲 随机抽 50 词；📕 错题本（显示到期数量）；➕ 导入词库；词根词缀表；使用说明 |
| 配置页 | 每组词数（默认 50）、先浏览后测验 / 直接测验、浏览顺序、4 或 6 个选项、每词浏览时长 |
| 会话页 | 上半段浏览（词 + 音标 + 中英释义 + 例句 + 词根），下半段测验（看词选英文释义，即时判分） |
| 结果页 | 环形正确率、对/错/未答/用时、成绩网格（点格子复盘）、复盘全部 / 同库再来一组 |
| 错题本 | 按词库分组、到期置顶高亮、显示 ✗次数 / Lv.级别 / 下次复习时间，可发音、立即复习、删除 |

## 发音（口音跟着词库走）

用浏览器 Web Speech API 朗读。**每个词库有自己的口音**：词库 JS 顶层的 `locale` 字段（`"en-GB"` 或 `"en-US"`）
决定这组词用哪个 voice，不写就按 `en-GB`（经济学人那份就是这么出厂的）。
两种口音各挑一个本机 voice，互不串味：

- `en-GB`（伦敦音）：Daniel → Arthur → Martha → Google UK English Female/Male →
  Kate / Serena / Sonia / Libby / Olivia / Hazel → Reid / Reed / Flo / Sandy / Shelley / Rocko
- `en-US`（通用美音）：Alex → Samantha → Ava → Google US English → Aria / Jenny / Guy →
  Allison / Nicky / Zira / Susan

首页底部按口音分行列出实际选中的 voice，会话状态栏显示当前这组词该用的那个；
本机装不上某个口音的 voice 时会回落到另一个引擎并打 **⚠ 这不是 en-US voice**。
混合池与错题本复习跨词库时，每个词按自己词库的口音朗读。
点 🔊、点单词本身、或按 <kbd>P</kbd> 播放；例句旁的小喇叭朗读例句。
词条里若填了 `audio`（本地 mp3 相对路径或 data URI），优先播放音频，失败自动回退合成语音。

macOS 建议用 Safari 或 Chrome（本机验证用的是 Daniel 与 Samantha）。
iPad 上要先在 设置 → 辅助功能 → 朗读内容 → 声音 里下载对应口音，否则只会走回落并打 ⚠。

## 错题本与记忆曲线

答错、浏览时点「没记住」、或按 <kbd>M</kbd> 标记的词进错题本，间隔为：

```
20 分钟 → 1 小时 → 9 小时 → 1 天 → 2 天 → 6 天 → 14 天 → 30 天
```

复习时自评评级：

| 评级 | 效果 |
|---|---|
| 没记住 Again | 归零，回到 20 分钟 |
| 模糊 Hard | 保持本级，间隔 ×1.2 |
| 记住 Good | 升一级 |
| 牢记 Easy | 跳两级，间隔再 ×2 |

30 天那一档再答对，该词毕业并自动移出错题本（会弹 🎓 提示）。
到期单词在错题本里置顶并加橙色高亮，可「复习全部到期」，也可单点「立即复习」。

存储键：`vocab_wrongbook_v1`（错题本）、`vocab_custom_banks_v1`（导入的自定义词库）。

## 快捷键

<kbd>A</kbd>–<kbd>F</kbd> / <kbd>1</kbd>–<kbd>6</kbd> 选释义（复习答完后同样这几个键＝评级）·
<kbd>P</kbd> 发音 · <kbd>Enter</kbd> 下一个 · <kbd>←</kbd> <kbd>→</kbd> 前后翻页 ·
<kbd>T</kbd> 切换中文 · <kbd>M</kbd> 标记 · <kbd>Esc</kbd> 关弹窗

## 添加你自己的词库

**方式一：文件登记（推荐给大批量词表）**

```bash
cd vocab-app
python3 tools/convert_csv_vocab.py 我的词表.csv --id mywords --label "我的词库 300 词"
```

脚本会生成 `vocab/mywords.js` 并在 `vocab/manifest.js` 登记一行，刷新首页就能看到。
CSV 表头认这些列（每个字段都有一串中英文别名，缺的留空）：
`word/单词/vocab`、`phonetic/音标/ipa`、`pos/词性`、`def_en/英文释义/释义/解释`、
`def_zh/中文释义/中文/翻译`、`example/例句/sentence`、`example_zh/例句中文/例句翻译/例句译文`、
`etymology/词根/词根词缀/记忆法/备注`、`tags/标签/分类`、`audio/音频`。
首页「➕ 导入词库文件」用的是同一套别名表。格式见 `tools/sample_words.csv`。

**方式二：首页直接导入**

点「➕ 导入词库文件」，选 `.csv` / `.tsv` / `.json` / 词库 `.js`。
导入的词库存进浏览器本地，换电脑不会跟过去（可在词库 JS 里保留一份原始文件）。

**方式三：手写词库 JS**

```js
// vocab/mywords.js
window.registerVocab({
  id: "mywords",
  label: "我的词库 300 词",
  source: "来源说明",
  words: [{
    word: "apportion", phonetic: "/əˈpɔːʃn/", pos: "v.",
    def_en: "To divide and distribute something according to a plan or share.",
    def_zh: "分摊；分配",
    example: "The ministry will apportion the funds among the provinces.",
    example_zh: "部会将资金在各州之间分配。",
    etymology: "ap-(去) + portion(份)",
    tags: ["财政"], audio: ""
  }]
});
```

然后在 `vocab/manifest.js` 的数组里加一行：

```js
{ id: "mywords", label: "我的词库 300 词", file: "vocab/mywords.js" },
```

**口音：`locale` 字段**

词库 JS 里可以写 `locale: "en-US"`（通用美音）或 `en-GB`（伦敦音，不写就是它）。
发音引擎按当前词库的 `locale` 各选一个本机 voice：`en-GB` 优先 Daniel/Arthur/Kate 等，`en-US` 优先 Alex/Samantha/Ava 等。
本机只装了另一种口音时不会报错，照读，但首页脚注和状态栏会标 ⚠ 提示该去系统「辅助功能 → 朗读内容」补语音。
导入的词库也认这个字段：导入词库 JS（`registerVocab` 那份）或带 `locale` 的 JSON 都会保留口音设置；
CSV / TSV 没有这一列，导入后一律按英音读。

## 重新生成经济学人词库

现收录 443 词：从 75 篇朗读稿的 68,925 词里按 Zipf 1.2–4.0 挑出 700 个候选，
再由逐词判定按 `VOCAB_SPEC.md` 决定收录（443 收 / 257 判为太专、太透明或只是屈折形式而跳过，每个跳过都留了理由）。

```bash
cd ../economist-audio
.venv/bin/python extract_vocab.py          # Zipf 1.2–4.0 挑候选 → vocab/candidates.tsv
.venv/bin/python make_vocab_batches.py     # 切成 50 词一批 → vocab/batches/（批次号只增不复用）
# 按 VOCAB_SPEC.md 产出 vocab/parts/vocab_NN.jsonl 后：
.venv/bin/python check_vocab.py            # 门禁：行数/字段/RP 音标/例句忠实度
.venv/bin/python build_wordbank.py         # 写 ../vocab-app/vocab/eco_2026_10_31.js
.venv/bin/python verify_bank.py            # 出厂检查：成品词库里不许有栏头/日期残留
```

`build_wordbank.py` 落盘前会跟上一版成品比词表：**有任何已交付的词在新装配里消失就拒绝覆盖**（exit 1 并列出词名），
确认是有意精简才加 `--allow-drop`。老工单被误删时用 `make_vocab_batches.py --restore-inputs` 按 `parts/` 词序找回。
细节与坑清单见 `~/Desktop/handoff/grabword.md`。

`build_wordbank.py` 会按原文（`text/NN-*.txt` 与对应 `.zh.txt`）重建被朗读稿粘连上标题栏的例句，
并把每一次改写打印出来；重建不了的例句直接留空，不会编造。

## 重新生成纽约客词库

现收录 454 词（`locale: "en-US"`，音标是 IPA 通用美音）：从 20 篇朗读稿按同样的 Zipf 1.2–4.0 挑出 700 个候选，
再逐词判定（454 收 / 246 跳过）。命令与门禁见 `~/Desktop/handoff/newyorker-audio.md` §10，
移植差异与 manifest 合并护栏见 `~/Desktop/handoff/grabword.md` §11。

**两个刊物共用 `vocab/manifest.js`**：纽约客那侧的 `build_wordbank.py` 是"合并写"（保留别人那一行，
解析不出来的行会直接拒绝改写），经济学人那侧目前仍是"整写"。所以任何一侧重新装配之后，
都要跑一次出厂检查（它会核对"磁盘上的词库 ↔ manifest 登记"），少一行会当场报错，再补跑另一侧的装配即可。
