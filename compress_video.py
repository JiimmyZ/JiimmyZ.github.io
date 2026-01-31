"""
压缩视频文件以符合 Cloudinary 限制（100MB）

使用方法:
    python compress_video.py content/travelogue/camino/ch8/VID_20250703_100502.mp4
"""

import subprocess
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"


def check_ffmpeg():
    """检查 FFmpeg 是否安装"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def compress_video(input_path, output_path=None, target_size_mb=95):
    """
    压缩视频文件

    Args:
        input_path: 输入视频路径
        output_path: 输出视频路径（如果为None，则自动生成）
        target_size_mb: 目标文件大小（MB），默认95MB（留5MB余量）
    """
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"Error: File not found: {input_path}")
        return False

    # 获取原始文件大小
    original_size_mb = input_file.stat().st_size / 1024 / 1024
    print(f"Original file size: {original_size_mb:.2f} MB")

    if original_size_mb <= target_size_mb:
        print("File is already within limit, no compression needed.")
        return True

    # 生成输出文件名
    if output_path is None:
        output_path = (
            input_file.parent / f"{input_file.stem}_compressed{input_file.suffix}"
        )

    output_file = Path(output_path)

    # 计算目标比特率（粗略估算）
    # 假设视频时长约等于文件大小/比特率
    # 使用 CRF (Constant Rate Factor) 进行质量压缩
    # CRF 23 是高质量，CRF 28 是中等质量

    print("\nCompressing video...")
    print(f"Output: {output_file}")
    print("This may take several minutes...")

    # FFmpeg 命令
    # -crf 23: 高质量压缩（可调整到 25-28 以获得更小文件）
    # -preset slow: 更好的压缩率（但更慢）
    # -c:v libx264: 使用 H.264 编码
    # -c:a aac: 音频编码
    # -b:a 128k: 音频比特率

    # Use more aggressive compression settings
    # Start with CRF 28 for better compression, can increase to 30 if needed
    cmd = [
        "ffmpeg",
        "-i",
        str(input_file),
        "-c:v",
        "libx264",
        "-crf",
        "28",  # More aggressive: 28=lower quality but smaller file
        "-preset",
        "slow",  # Better compression ratio (slower but smaller)
        "-vf",
        "scale='if(gt(iw,1920),1920,-1)':'if(gt(ih,1080),1080,-1)'",  # Scale down if >1080p
        "-c:a",
        "aac",
        "-b:a",
        "96k",  # Lower audio bitrate for smaller file
        "-movflags",
        "+faststart",  # Optimize for web playback
        "-y",  # Overwrite output file
        str(output_file),
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # 检查输出文件大小
        if output_file.exists():
            compressed_size_mb = output_file.stat().st_size / 1024 / 1024
            print("\nCompression complete!")
            print(f"Original: {original_size_mb:.2f} MB")
            print(f"Compressed: {compressed_size_mb:.2f} MB")
            print(
                f"Reduction: {((1 - compressed_size_mb / original_size_mb) * 100):.1f}%"
            )

            if compressed_size_mb <= target_size_mb:
                print(
                    f"\n[SUCCESS] File is now {compressed_size_mb:.2f} MB (under {target_size_mb} MB limit)"
                )
                return True
            else:
                print(
                    f"\n[WARNING] File is still {compressed_size_mb:.2f} MB (over {target_size_mb} MB limit)"
                )
                print("Attempting more aggressive compression with CRF 30...")
                
                # Try even more aggressive compression
                cmd_aggressive = [
                    "ffmpeg",
                    "-i",
                    str(input_file),
                    "-c:v",
                    "libx264",
                    "-crf",
                    "30",  # Very aggressive compression
                    "-preset",
                    "slow",
                    "-vf",
                    "scale='if(gt(iw,1280),1280,-1)':'if(gt(ih,720),720,-1)'",  # Scale to 720p max
                    "-c:a",
                    "aac",
                    "-b:a",
                    "64k",  # Very low audio bitrate
                    "-movflags",
                    "+faststart",
                    "-y",
                    str(output_file),
                ]
                
                try:
                    subprocess.run(cmd_aggressive, check=True, capture_output=True, text=True)
                    if output_file.exists():
                        compressed_size_mb = output_file.stat().st_size / 1024 / 1024
                        print(f"Second attempt: {compressed_size_mb:.2f} MB")
                        if compressed_size_mb <= target_size_mb:
                            print(
                                f"\n[SUCCESS] File is now {compressed_size_mb:.2f} MB (under {target_size_mb} MB limit)"
                            )
                            return True
                except subprocess.CalledProcessError:
                    pass
                
                print("Could not compress below 100MB limit. File may be too long or high quality.")
                return False
        else:
            print("Error: Output file was not created")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        print(f"FFmpeg output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: FFmpeg not found!")
        print("Please install FFmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python compress_video.py <video_file> [output_file]")
        print("\nExample:")
        print(
            "  python compress_video.py content/travelogue/camino/ch8/VID_20250703_100502.mp4"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not in PATH")
        print("Please install FFmpeg first:")
        print("  Windows: choco install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        sys.exit(1)

    success = compress_video(input_path, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
