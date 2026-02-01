# Ebook Generator - 開發工作流程與檢查清單

## 目標
避免反覆修正錯誤，確保每次修改都能一次到位。

## 修改前檢查清單

### 1. 問題分析階段
- [ ] **完整理解問題**：閱讀錯誤訊息、用戶描述、相關日誌
- [ ] **確認問題範圍**：問題影響哪些文件、哪些功能
- [ ] **檢查相關文件**：閱讀所有相關的源文件，理解現有邏輯
- [ ] **理解系統架構**：確認修改不會影響其他部分
- [ ] **檢查歷史記錄**：查看 PROGRESS.md 中是否有相關問題記錄

### 2. 方案設計階段
- [ ] **多方案比較**：考慮至少 2-3 種解決方案
- [ ] **評估副作用**：確認修改不會破壞現有功能
- [ ] **檢查依賴關係**：確認修改不會影響其他模組
- [ ] **驗證參數/API**：確認使用的參數、API 版本是否正確（如 Pandoc 版本）

### 3. 實作階段
- [ ] **小步修改**：一次只修改一個明確的問題
- [ ] **保留測試點**：修改後可以快速驗證
- [ ] **添加註釋**：說明「為什麼」這樣修改，而不只是「做了什麼」

### 4. 驗證階段
- [ ] **語法檢查**：運行 linter 檢查語法錯誤
- [ ] **單元測試**：如果可能，先測試修改的函數
- [ ] **整合測試**：運行完整流程驗證
- [ ] **邊界情況**：檢查極端情況（如空文件、特殊字符）

## 常見陷阱與預防

### 1. API/工具版本變更
**問題**：Pandoc 3.8+ 棄用 `--epub-chapter-level`，改用 `--split-level`
**預防**：
- 檢查工具版本：`pandoc --version`
- 查閱最新文檔：`pandoc --help | Select-String "split"`
- 測試參數有效性：先用簡單命令測試

### 2. 標題層級混亂
**問題**：章節標題與內容標題同級，導致目錄結構錯誤
**預防**：
- 在修改前先檢查現有標題結構：`grep "^#\+ " merged_file.md`
- 理解 Pandoc TOC 生成邏輯
- 確認修改後的標題層級是否符合預期

### 3. 路徑與環境問題
**問題**：Windows PowerShell 語法、PATH 環境變數
**預防**：
- 確認執行環境（PowerShell vs Bash）
- 檢查工具是否在 PATH 中
- 使用絕對路徑或確認相對路徑正確

### 4. 文件編碼問題
**問題**：UTF-8 編碼、Windows 換行符
**預防**：
- 明確指定編碼：`read_text(encoding='utf-8')`
- 注意 Windows vs Unix 換行符差異

## 修改流程範例

### 範例：修改章節合併邏輯

1. **問題分析**
   ```
   - 閱讀用戶描述
   - 檢查 merge_chapters.py 現有邏輯
   - 查看合併後的檔案結構
   - 理解 Pandoc 如何處理標題
   ```

2. **方案設計**
   ```
   方案 A：提升內容標題級別（選擇此方案）
   方案 B：降低章節標題級別（會影響其他部分）
   方案 C：使用 Pandoc 後處理（複雜度高）
   ```

3. **實作**
   ```python
   # 添加函數前先測試正則表達式
   # 確認能正確匹配所有標題
   # 確認不會誤匹配其他內容
   ```

4. **驗證**
   ```bash
   # 1. 語法檢查
   python -m py_compile merge_chapters.py
   
   # 2. 運行合併
   python merge_chapters.py
   
   # 3. 檢查結果
   grep "^#\+ " merged/camino_merged.md | head -20
   
   # 4. 完整流程測試
   python main.py
   ```

## 快速檢查命令

### 檢查合併檔案結構
```powershell
# 檢查所有章節標題
grep "^# Chapter" merged/camino_merged.md

# 檢查標題層級分布
grep "^#\+ " merged/camino_merged.md | Select-String -Pattern "^#" | ForEach-Object { $_.Matches[0].Value } | Group-Object | Sort-Object Count -Descending
```

### 檢查 Pandoc 參數
```powershell
# 檢查 Pandoc 版本
pandoc --version

# 檢查參數幫助
pandoc --help | Select-String "split-level"
pandoc --help | Select-String "epub-chapter"
```

### 檢查生成結果
```powershell
# 檢查 EPUB 檔案
Get-Item output/camino_pilgrim.epub | Format-List Name, Length, LastWriteTime

# 檢查合併檔案大小
Get-Item merged/camino_merged.md | Format-List Length
```

## 提交前最終檢查

- [ ] 所有相關文件都已修改
- [ ] 沒有遺留的測試代碼或註釋
- [ ] PROGRESS.md 已更新
- [ ] 代碼通過 linter 檢查
- [ ] 完整流程可以成功執行
- [ ] 修改符合用戶需求

## 記錄與文檔

每次修改後：
1. 更新 PROGRESS.md 記錄問題與解決方案
2. 在代碼中添加註釋說明「為什麼」這樣修改
3. 記錄遇到的陷阱和解決方法

---

**原則**：寧可多花時間在分析階段，也不要反覆修正錯誤。
