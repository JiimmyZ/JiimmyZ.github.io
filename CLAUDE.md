# JZ隨筆 — Agent 指南

Hugo 靜態部落格（PaperMod 主題），繁體中文，單人維護。本檔只放指標與最容易踩雷的規則，細節在下表對應的文件裡。

## 先看哪份文件

| 要找什麼 | 看哪裡 |
|----------|--------|
| 網站設定／選單／Giscus／不蒜子 | [`hugo.toml`](hugo.toml) |
| 操作手冊（內容放哪、部署流程、媒體怎麼處理） | [`README.md`](README.md) |
| 近期決策與現況 | [`context.md`](context.md) |
| 歷史 session、遷移、架構決策（ADR） | [`LEGACY.md`](LEGACY.md) |
| 著作權與授權 | [`COPYRIGHT.md`](COPYRIGHT.md) |

## 最容易忘的規則

- 媒體上傳／換連結只認 [`media_processor.py`](media_processor.py)，不要用舊腳本或手動塞大量原始媒體進 git（媒體放 Cloudinary CDN）
- 不要擅自加第二套評論系統、協作流程或「貢獻指南」
- 不要提交 `.env` 或 `public/`（`public/` 是建置產物）
- **不要加開源 LICENSE 檔**（MIT／Apache 等）。這是公開 repo，根目錄放開源授權會被當成連 `content/` 的創作一起釋出，而且收不回來。理由見 [`COPYRIGHT.md`](COPYRIGHT.md)
- 內容 md（詩詞／小說／雜感／賞析／遊記）新增或修改：完成後 commit + push；純功能開發可以先留在本機，等明確決定再 push

## Git / PR 慣例

- push 完分支後，除非使用者特別說要 fork，否則自動對 `main` 開 PR，不用每次都問
- `.github/workflows/deploy.yml`：`pull_request` 對 main 時會跑 `test` + `lint`；`build`／`deploy` 只在 push main 時執行
- 開 PR 後可訂閱 PR 活動；CI 綠燈、沒有未解決的 review 意見時可直接合併，不用每次額外確認
