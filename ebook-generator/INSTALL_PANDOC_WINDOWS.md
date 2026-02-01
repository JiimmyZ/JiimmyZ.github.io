# Windows 安裝 Pandoc 指南

## 方法 1: 使用 winget (Windows 10/11 內建)

1. 以**管理員身份**開啟 PowerShell
2. 執行：
   ```powershell
   winget install --id JohnMacFarlane.Pandoc -e
   ```
3. 輸入 `Y` 同意條款

## 方法 2: 使用 Chocolatey (需要管理員權限)

1. 以**管理員身份**開啟 PowerShell
2. 執行：
   ```powershell
   choco install pandoc -y
   ```

## 方法 3: 手動下載安裝 (推薦，最簡單)

1. 前往：https://github.com/jgm/pandoc/releases/latest
2. 下載 `pandoc-x.x.x-windows-x86_64.msi` (最新版本)
3. 雙擊安裝程式執行安裝
4. 安裝完成後，重新開啟 PowerShell
5. 驗證安裝：執行 `pandoc --version`

## 驗證安裝

安裝完成後，在新的 PowerShell 視窗執行：
```powershell
pandoc --version
```

如果顯示版本號，表示安裝成功！

## 注意事項

- 安裝後可能需要重新開啟終端機才能使用
- 如果 `pandoc --version` 仍無法執行，請檢查 PATH 環境變數
