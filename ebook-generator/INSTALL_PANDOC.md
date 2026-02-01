# 安裝 Pandoc

## Windows 安裝方式

### 方法 1: 使用 Chocolatey (推薦)
```powershell
choco install pandoc
```

### 方法 2: 手動下載安裝
1. 前往 https://github.com/jgm/pandoc/releases/latest
2. 下載 `pandoc-x.x.x-windows-x86_64.msi`
3. 執行安裝程式
4. 確認安裝：在 PowerShell 執行 `pandoc --version`

### 方法 3: 使用 Scoop
```powershell
scoop install pandoc
```

安裝完成後，重新執行 `python main.py` 即可生成 EPUB。
