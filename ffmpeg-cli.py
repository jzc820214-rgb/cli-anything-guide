#!/usr/bin/env python3
"""
FFmpeg CLI - 媒体处理工具
功能：视频压缩、格式转换、提取音频、裁剪、信息查看
"""
import subprocess
import argparse
import sys
import os
import json
from pathlib import Path

def run_ffmpeg(args_list, description="FFmpeg"):
    """运行 FFmpeg 命令"""
    cmd = ['ffmpeg', '-y'] + args_list
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "处理超时"
    except Exception as e:
        return False, str(e)

def compress_video(input_file, output_file=None, quality="medium"):
    """智能压缩视频"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.compressed.mp4')
    
    # 根据质量设置参数
    presets = {
        "high": {"crf": "18", "preset": "slow"},    # 高质量
        "medium": {"crf": "23", "preset": "medium"}, # 中等（默认）
        "low": {"crf": "28", "preset": "fast"}      # 高压缩
    }
    preset = presets.get(quality, presets["medium"])
    
    args = [
        '-i', str(input_path),
        '-vcodec', 'libx264',
        '-crf', preset["crf"],
        '-preset', preset["preset"],
        '-acodec', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        str(output_file)
    ]
    
    print(f"🗜️  压缩视频 ({quality} 质量)...")
    success, error = run_ffmpeg(args)
    
    if success:
        original_size = input_path.stat().st_size / (1024*1024)
        new_size = Path(output_file).stat().st_size / (1024*1024)
        ratio = (1 - new_size/original_size) * 100
        print(f"✅ 压缩完成: {output_file}")
        print(f"   原大小: {original_size:.1f} MB → 新大小: {new_size:.1f} MB (节省 {ratio:.1f}%)")
        return True
    else:
        print(f"❌ 压缩失败: {error[:200]}")
        return False

def extract_audio(input_file, output_file=None, format="mp3"):
    """从视频提取音频"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix(f'.{format}')
    
    # 根据格式设置编码器
    codecs = {
        "mp3": ("libmp3lame", "192k"),
        "aac": ("aac", "192k"),
        "wav": ("pcm_s16le", None),
        "flac": ("flac", None)
    }
    
    codec, bitrate = codecs.get(format, ("libmp3lame", "192k"))
    
    args = ['-i', str(input_path), '-vn', '-acodec', codec]
    if bitrate:
        args.extend(['-b:a', bitrate])
    args.append(str(output_file))
    
    print(f"🎵 提取音频 ({format})...")
    success, error = run_ffmpeg(args)
    
    if success:
        size = Path(output_file).stat().st_size / (1024*1024)
        print(f"✅ 提取完成: {output_file} ({size:.1f} MB)")
        return True
    else:
        print(f"❌ 提取失败: {error[:200]}")
        return False

def video_to_gif(input_file, output_file=None, fps=10, scale=480):
    """视频转 GIF"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.gif')
    
    # 使用调色板优化 GIF 质量
    args = [
        '-i', str(input_path),
        '-vf', f'fps={fps},scale={scale}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse',
        '-loop', '0',
        str(output_file)
    ]
    
    print(f"🎬 转换为 GIF ({fps}fps, {scale}px)...")
    success, error = run_ffmpeg(args)
    
    if success:
        size = Path(output_file).stat().st_size / 1024
        print(f"✅ 转换完成: {output_file} ({size:.1f} KB)")
        return True
    else:
        print(f"❌ 转换失败: {error[:200]}")
        return False

def cut_video(input_file, start_time, duration, output_file=None):
    """裁剪视频"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.cut.mp4')
    
    args = [
        '-i', str(input_path),
        '-ss', start_time,
        '-t', str(duration),
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        str(output_file)
    ]
    
    print(f"✂️  裁剪视频 (从 {start_time}, 持续 {duration}秒)...")
    success, error = run_ffmpeg(args)
    
    if success:
        size = Path(output_file).stat().st_size / (1024*1024)
        print(f"✅ 裁剪完成: {output_file} ({size:.1f} MB)")
        return True
    else:
        print(f"❌ 裁剪失败: {error[:200]}")
        return False

def video_info(input_file):
    """查看视频信息"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    # 使用 ffprobe 获取信息
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration,size,bit_rate',
        '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
        '-of', 'json',
        str(input_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        print(f"📹 {input_file}")
        print(f"   大小: {input_path.stat().st_size / (1024*1024):.1f} MB")
        
        if 'format' in data:
            fmt = data['format']
            if 'duration' in fmt:
                duration = float(fmt['duration'])
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                print(f"   时长: {minutes}:{seconds:02d}")
            if 'bit_rate' in fmt:
                bitrate = int(fmt['bit_rate']) / 1000
                print(f"   码率: {bitrate:.0f} kbps")
        
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                print(f"   视频: {stream.get('codec_name', 'N/A')}")
                print(f"   分辨率: {stream.get('width', 'N/A')}x{stream.get('height', 'N/A')}")
                fps = eval(stream.get('r_frame_rate', '0/1'))
                print(f"   帧率: {fps:.1f} fps")
            elif stream.get('codec_type') == 'audio':
                print(f"   音频: {stream.get('codec_name', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ 获取信息失败: {e}")
        return False

def thumbnail(input_file, time_point="00:00:01", output_file=None):
    """提取视频封面"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.jpg')
    
    args = [
        '-ss', time_point,
        '-i', str(input_path),
        '-vframes', '1',
        '-q:v', '2',
        str(output_file)
    ]
    
    print(f"🖼️  提取封面 (时间点: {time_point})...")
    success, error = run_ffmpeg(args)
    
    if success:
        size = Path(output_file).stat().st_size / 1024
        print(f"✅ 封面已保存: {output_file} ({size:.1f} KB)")
        return True
    else:
        print(f"❌ 提取失败: {error[:200]}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='FFmpeg CLI - 媒体处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s compress video.mp4                    # 智能压缩
  %(prog)s compress video.mp4 -q low             # 高压缩比
  %(prog)s audio video.mp4 -o music.mp3          # 提取音频
  %(prog)s gif video.mp4 -f 15 -s 320            # 转 GIF (15fps, 320px)
  %(prog)s cut video.mp4 00:01:30 60             # 从1分30秒裁剪60秒
  %(prog)s info video.mp4                        # 查看视频信息
  %(prog)s thumb video.mp4 -t 00:00:05           # 提取第5秒封面
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # compress 命令
    compress_parser = subparsers.add_parser('compress', help='压缩视频')
    compress_parser.add_argument('input', help='输入视频文件')
    compress_parser.add_argument('-o', '--output', help='输出文件')
    compress_parser.add_argument('-q', '--quality', choices=['high', 'medium', 'low'],
                                 default='medium', help='压缩质量 (默认: medium)')
    
    # audio 命令
    audio_parser = subparsers.add_parser('audio', help='提取音频')
    audio_parser.add_argument('input', help='输入视频文件')
    audio_parser.add_argument('-o', '--output', help='输出文件')
    audio_parser.add_argument('-f', '--format', choices=['mp3', 'aac', 'wav', 'flac'],
                              default='mp3', help='音频格式 (默认: mp3)')
    
    # gif 命令
    gif_parser = subparsers.add_parser('gif', help='视频转 GIF')
    gif_parser.add_argument('input', help='输入视频文件')
    gif_parser.add_argument('-o', '--output', help='输出文件')
    gif_parser.add_argument('-f', '--fps', type=int, default=10, help='帧率 (默认: 10)')
    gif_parser.add_argument('-s', '--scale', type=int, default=480, help='宽度像素 (默认: 480)')
    
    # cut 命令
    cut_parser = subparsers.add_parser('cut', help='裁剪视频')
    cut_parser.add_argument('input', help='输入视频文件')
    cut_parser.add_argument('start', help='开始时间 (HH:MM:SS 或秒数)')
    cut_parser.add_argument('duration', type=int, help='持续时间 (秒)')
    cut_parser.add_argument('-o', '--output', help='输出文件')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看视频信息')
    info_parser.add_argument('input', help='输入视频文件')
    
    # thumb 命令
    thumb_parser = subparsers.add_parser('thumb', help='提取视频封面')
    thumb_parser.add_argument('input', help='输入视频文件')
    thumb_parser.add_argument('-o', '--output', help='输出文件')
    thumb_parser.add_argument('-t', '--time', default='00:00:01', 
                              help='时间点 (默认: 00:00:01)')
    
    args = parser.parse_args()
    
    if args.command == 'compress':
        compress_video(args.input, args.output, args.quality)
    elif args.command == 'audio':
        extract_audio(args.input, args.output, args.format)
    elif args.command == 'gif':
        video_to_gif(args.input, args.output, args.fps, args.scale)
    elif args.command == 'cut':
        cut_video(args.input, args.start, args.duration, args.output)
    elif args.command == 'info':
        video_info(args.input)
    elif args.command == 'thumb':
        thumbnail(args.input, args.time, args.output)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
