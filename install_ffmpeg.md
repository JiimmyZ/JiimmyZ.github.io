# 安装 FFmpeg 指南

## 方法 1: 使用 Chocolatey（推荐）

如果你已经安装了 Chocolatey：

```powershell
# 以管理员身份运行 PowerShell，然后执行：
choco install ffmpeg
```

如果没有安装 Chocolatey，先安装它：
```powershell
# 以管理员身份运行 PowerShell，然后执行：
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

## 方法 2: 使用 Scoop

如果你已经安装了 Scoop：

```powershell
scoop install ffmpeg
```

## 方法 3: 手动下载安装

1. 访问 https://www.gyan.dev/ffmpeg/builds/
2. 下载 "ffmpeg-release-essentials.zip"
3. 解压到 `C:\ffmpeg`
4. 将 `C:\ffmpeg\bin` 添加到系统 PATH 环境变量
5. 重启终端

## 验证安装

安装完成后，运行以下命令验证：

```powershell
ffmpeg -version
```

如果显示版本信息，说明安装成功！

## 然后压缩视频

安装 FFmpeg 后，运行：

```powershell
python compress_video.py content/travelogue/camino/ch8/VID_20250703_100502.mp4
```
