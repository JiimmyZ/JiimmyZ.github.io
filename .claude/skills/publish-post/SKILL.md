---
name: publish-post
description: 把 JZ 寫好的作品（詩詞、雜感、小說、賞析、遊記）上架到 Hugo 部落格「JZ隨筆」——建檔、補 frontmatter、commit、開 PR、CI 綠燈後合併。當 JZ 說「幫我把以下內容發佈到我的網站」「這首詩幫我發上去」「新增一篇到部落格」，或直接丟一段詩／散文過來、語氣像是要上架時，就用這個 skill。他不一定會說出「發佈」兩個字——只要看起來是把創作交給你放上站，先問一句要不要跑這個 skill 再動手。
---

# 發佈作品到 JZ隨筆

JZ 負責寫，你負責上架。他把作品丟過來，你把它變成 `content/` 底下格式正確的 md 檔並推上線。

## 先讀這段：為什麼要慢一點

這個流程有五種失敗方式，**CI 一個都抓不到**——測試會過、網站會建置成功、部署會綠燈，但東西是錯的：

| 失敗 | 讀者看到什麼 |
|------|-------------|
| 詩句行尾少了兩個空格 | 整首詩擠成一整段，斷行全沒了 |
| 分類放錯 | 詩跑到雜感區，或反過來 |
| summary 是你編的 | 首頁列表和搜尋結果的第一印象不是 JZ 的意思 |
| 檔名撞名 | 靜靜蓋掉一篇舊作，沒有任何警告 |
| 原始媒體檔進 git | repo 肥大——ADR-001 就是在收拾這個爛攤子 |

`pytest` 和 `ruff` 只檢查 Python 腳本，完全不看 `content/`。所以這裡沒有安全網，只有你的細心。寧可多問一句，不要猜。

## 三件事永遠不要自己決定

**分類、tags、summary 都要問 JZ。** 這三個不是 metadata，是編輯判斷——是他的聲音，不是你的。

而且有前科：`content/essay/` 裡的 12 篇，全都是先被放進詩詞區、後來才搬出來的。詩詞和雜感在這個站的界線本來就模糊（極短的哲思三行，算詩還是雜感？只有 JZ 知道），所以不要相信自己的第一直覺。

問的成本是一則訊息。猜錯的成本是東西已經上線了，而且他要好幾週後才會發現。

### summary 的特例：可以提議，但不能擅自用

短篇作品的既有慣例是 **summary 就是正文，換行改成空格**。例如：

```toml
summary = "快樂不值得追求 痛苦不值得畏懼"
```
正文就是那兩行。

所以短篇可以這樣問：「summary 我照慣例幫你帶成『快樂不值得追求 痛苦不值得畏懼』，可以嗎？」——他點頭你才寫進去。

長篇散文和遊記不適用，那些的 summary 是真的手寫概述（例如遊記 ch3 的 `"通勤、住宿選擇與實用網站、App整理"`）。長篇一律請他給。

### tags 先看現有的

先撈出目前用過的標籤，讓 JZ 從裡面挑，避免生出「離別／別離」這種意思一樣的重複標籤：

```bash
grep -h "^tags" content/*/*.md content/*/*/*/index.md 2>/dev/null \
  | sed 's/tags = //' | tr -d '[]"' | tr ',' '\n' \
  | sed 's/^ *//;s/ *$//' | grep -v '^$' | sort | uniq -c | sort -rn
```

常見的有：絕句、哲思、新詩、情詩、朝聖之路、Camino、社會。他要開新標籤當然可以，但值得先確認是不是跟舊的重複。

## 放哪裡

| 類型 | 路徑 |
|------|------|
| 詩詞 | `content/poetry/標題.md` |
| 雜感 | `content/essay/標題.md` |
| 小說 | `content/novel/標題.md` |
| 賞析 | `content/review/標題.md` |
| 遊記 | `content/travelogue/系列/章節/index.md`（page bundle，見最後一節） |

檔名就是標題。**建檔前先確認沒撞名**，而且要掃全站不是只掃目標資料夾——同名作品可能躺在別的分類裡：

```bash
find content -name "標題.md"
```

有結果就停下來問 JZ：是要改標題、還是這篇要取代舊的。不要自己決定。

## Frontmatter 格式

以 `archetypes/` 底下的樣板為準（`archetypes/poetry.md` 等）。實際長這樣：

```toml
+++
date = '2026-08-25T11:30:00+08:00'
draft = false
title = '快樂'
layout = "single" 
categories = ["essay"]
tags = ["哲思", "新詩"]
summary = "快樂不值得追求 痛苦不值得畏懼"
+++
```

幾個要注意的：

- **`categories` 要跟所在資料夾一致**。放 `content/essay/` 就寫 `["essay"]`。這個欄位餵給 SEO 結構化資料和 Hugo 自動生成的 `/categories/` 分類頁，跟目錄不一致就會出現「人在雜感區、卻被標成詩詞」的矛盾（2026-08 才剛全站修正過一輪，別再讓它歪掉）。
- **`date` 用發布當下的台北時間**。容器預設是 UTC，要指定時區：
  ```bash
  TZ='Asia/Taipei' date '+%Y-%m-%dT%H:%M:%S%:z'
  ```
- **`draft = false`**——寫 true 的話網站上看不到。
- 檔案存成不帶 BOM 的 UTF-8。舊檔有 13 個帶 BOM，那是歷史遺留，不要學。

## 正文格式

詩詞和短篇雜感有兩條慣例，都很容易漏：

**1. 每行結尾兩個空格。** 這是 Markdown 的強制換行語法，少了它整首詩會變成一段連續文字。這是最常出包的地方，因為肉眼看不出來。

**2. 結尾留一行 `自註:`**（後面留空，JZ 之後自己填）。

完整範例：

```markdown
+++
（frontmatter）
+++

快樂不值得追求··
痛苦不值得畏懼··

自註:
```

（`·` 代表空格，實際寫的是真的空白字元）

寫完一定要驗一下，`$` 前面有兩個空格才是對的：

```bash
cat -A content/poetry/標題.md | sed -n '/^+++\$/,$p' | tail -n +2
```

長篇散文、遊記用一般 Markdown 就好，不需要這兩條。

## 發佈

容器裡**沒有裝 hugo**，所以無法本機預覽或 `hugo new`——直接寫檔案就好，不要浪費時間找 hugo。

按 `CLAUDE.md` 的慣例走，不需要另外請 JZ 確認：

1. `git status` 確認乾淨，然後把檔案加進去 commit
2. push 到目前分支
3. 對 `main` 開 PR
4. 訂閱 PR、等 CI（test + lint）綠燈
5. 綠燈且沒有未解決的 review 意見 → 直接合併

**如果目前分支對應的 PR 已經合併過了**，不能在上面疊新 commit。從最新的 main 重建同名分支再做：

```bash
git fetch origin main && git checkout -B <目前分支名> origin/main
```

（這在實務上很常遇到，因為同一個 session 連續發好幾篇時，前一篇的 PR 已經合併了。）

合併後 GitHub Actions 會自動建置並部署到 https://jiimmyz.github.io/ ，幾分鐘內上線。

## 遊記與媒體

遊記是 page bundle：`content/travelogue/系列/章節/index.md`，媒體檔跟 `index.md` 放同一層。

**媒體上傳這一步，雲端 session 做不到。** Cloudinary 憑證只存在 JZ 本機的 `.env`（刻意不進 git），所以在遠端容器裡跑 `media_processor.py upload` 一定會失敗。不要嘗試，也不要跟他要憑證。

正確做法是把文字部分處理好，然後把指令交給 JZ 在本機跑：

```bash
# 1. 把媒體檔放進 content/travelogue/系列/章節/ 底下，md 裡先用檔名引用
# 2. 上傳到 Cloudinary 並取得網址
python media_processor.py upload

# 3. 把 md 裡的本機路徑換成 Cloudinary 網址
python media_processor.py update-markdown

# 4. 超過 100MB 的影片要先壓（工具以 95MB 為目標）
python media_processor.py compress <影片檔>
```

跑完之後，md 裡的引用會變成 `https://res.cloudinary.com/...` 的網址，本機的原始媒體檔就可以刪掉了。

**不要把原始媒體 commit 進 git。** 影片副檔名已經在 `.gitignore` 裡，但**圖片沒有**——`content/travelogue/camino/ch1/` 到現在還躺著兩個沒清掉的 jpg。commit 前用 `git status` 看一眼有沒有圖片混進去。

媒體處理只認 `media_processor.py`，不要自己寫上傳腳本。
