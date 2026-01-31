# 处理大视频文件

## 问题
`VID_20250703_100502.mp4` 文件大小为 **115.6 MB**，超过了 Cloudinary 免费版的限制（100 MB）。

## 解决方案

### 选项 1: 压缩视频（推荐）
使用 FFmpeg 压缩视频文件：

```bash
# 安装 FFmpeg (如果还没有)
# Windows: choco install ffmpeg 或下载 https://ffmpeg.org/download.html

# 压缩视频（保持质量，减小文件大小）
ffmpeg -i content/travelogue/camino/ch8/VID_20250703_100502.mp4 \
  -c:v libx264 -crf 23 -c:a aac -b:a 128k \
  content/travelogue/camino/ch8/VID_20250703_100502_compressed.mp4
```

### 选项 2: 使用其他存储服务
- **GitHub Releases**: 上传大文件到 GitHub Releases
- **YouTube**: 上传到 YouTube，然后嵌入
- **Vimeo**: 上传到 Vimeo，然后嵌入

### 选项 3: 升级 Cloudinary 计划
升级到付费计划以支持更大的文件（>100MB）

### 选项 4: 保持本地文件
如果这个视频不常用，可以保持本地文件，只在需要时手动处理

## 推荐做法
我建议使用选项 1（压缩视频），这样可以：
- 保持在 Cloudinary 免费版限制内
- 保持所有媒体文件在同一个地方
- 自动优化和 CDN 加速

需要我帮你压缩这个视频吗？
