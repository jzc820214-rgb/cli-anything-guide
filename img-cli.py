#!/usr/bin/env python3
"""
Image CLI - 图片处理工具 (基于 Pillow)
功能：压缩、调整大小、加水印、格式转换、批量处理
"""
import argparse
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import glob

def get_image_info(image_path):
    """获取图片信息"""
    try:
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }
    except Exception as e:
        print(f"❌ 无法读取图片: {e}")
        return None

def compress_image(input_file, output_file=None, quality=85, max_size=None):
    """压缩图片"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.compressed.jpg')
    
    try:
        with Image.open(input_path) as img:
            # 转换为 RGB（处理 PNG 透明通道）
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # 如果指定了最大尺寸，先调整大小
            if max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # 保存并压缩
            img.save(output_file, 'JPEG', quality=quality, optimize=True)
        
        original_size = input_path.stat().st_size / 1024
        new_size = Path(output_file).stat().st_size / 1024
        ratio = (1 - new_size/original_size) * 100
        
        print(f"✅ 压缩完成: {output_file}")
        print(f"   原大小: {original_size:.1f} KB → 新大小: {new_size:.1f} KB (节省 {ratio:.1f}%)")
        return True
    except Exception as e:
        print(f"❌ 压缩失败: {e}")
        return False

def resize_image(input_file, output_file=None, width=None, height=None, scale=None):
    """调整图片大小"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.resized.jpg')
    
    try:
        with Image.open(input_path) as img:
            orig_width, orig_height = img.size
            
            # 计算新尺寸
            if scale:
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
            elif width and height:
                new_width, new_height = width, height
            elif width:
                new_height = int(height or (width * orig_height / orig_width))
                new_width = width
            elif height:
                new_width = int(width or (height * orig_width / orig_height))
                new_height = height
            else:
                print("❌ 请指定宽度、高度或缩放比例")
                return False
            
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存
            if resized.mode in ('RGBA', 'P'):
                resized = resized.convert('RGB')
            resized.save(output_file, 'JPEG', quality=95)
        
        print(f"✅ 调整完成: {output_file}")
        print(f"   {orig_width}x{orig_height} → {new_width}x{new_height}")
        return True
    except Exception as e:
        print(f"❌ 调整失败: {e}")
        return False

def add_watermark(input_file, text, output_file=None, position="bottom-right", opacity=128):
    """添加文字水印"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.watermarked.jpg')
    
    try:
        with Image.open(input_path).convert("RGBA") as img:
            # 创建水印层
            watermark = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 计算字体大小（根据图片宽度）
            font_size = max(20, img.width // 20)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            positions = {
                "top-left": (20, 20),
                "top-right": (img.width - text_width - 20, 20),
                "bottom-left": (20, img.height - text_height - 20),
                "bottom-right": (img.width - text_width - 20, img.height - text_height - 20),
                "center": ((img.width - text_width) // 2, (img.height - text_height) // 2)
            }
            pos = positions.get(position, positions["bottom-right"])
            
            # 绘制文字
            draw.text(pos, text, font=font, fill=(255, 255, 255, opacity))
            
            # 合并
            result = Image.alpha_composite(img, watermark)
            result = result.convert("RGB")
            result.save(output_file, 'JPEG', quality=95)
        
        print(f"✅ 水印添加完成: {output_file}")
        print(f"   文字: '{text}' @ {position}")
        return True
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        return False

def convert_format(input_file, output_file=None, format=None):
    """转换图片格式"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    # 自动确定输出格式
    if format:
        ext = f'.{format.lower()}'
    elif output_file:
        ext = Path(output_file).suffix.lower()
        format = ext[1:].upper()
    else:
        # 默认转 webp
        ext = '.webp'
        format = 'WEBP'
    
    if output_file is None:
        output_file = input_path.with_suffix(ext)
    
    format_map = {
        '.jpg': 'JPEG', '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.gif': 'GIF',
        '.webp': 'WEBP',
        '.bmp': 'BMP',
        '.tiff': 'TIFF', '.tif': 'TIFF'
    }
    
    save_format = format_map.get(ext, format)
    
    try:
        with Image.open(input_path) as img:
            # 处理透明通道
            if save_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            if save_format == 'WEBP':
                img.save(output_file, save_format, quality=85)
            elif save_format == 'JPEG':
                img.save(output_file, save_format, quality=95, optimize=True)
            else:
                img.save(output_file, save_format)
        
        orig_size = input_path.stat().st_size / 1024
        new_size = Path(output_file).stat().st_size / 1024
        print(f"✅ 转换完成: {output_file}")
        print(f"   格式: {save_format}, 大小: {orig_size:.1f} KB → {new_size:.1f} KB")
        return True
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

def crop_image(input_file, output_file=None, left=0, top=0, right=None, bottom=None):
    """裁剪图片"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.cropped.jpg')
    
    try:
        with Image.open(input_path) as img:
            width, height = img.size
            right = right or width
            bottom = bottom or height
            
            cropped = img.crop((left, top, right, bottom))
            
            if cropped.mode in ('RGBA', 'P'):
                cropped = cropped.convert('RGB')
            cropped.save(output_file, 'JPEG', quality=95)
        
        new_width = right - left
        new_height = bottom - top
        print(f"✅ 裁剪完成: {output_file}")
        print(f"   区域: ({left}, {top}, {right}, {bottom}) = {new_width}x{new_height}")
        return True
    except Exception as e:
        print(f"❌ 裁剪失败: {e}")
        return False

def batch_process(directory, operation, **kwargs):
    """批量处理图片"""
    path = Path(directory)
    if not path.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    # 支持的图片格式
    extensions = ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp')
    files = []
    for ext in extensions:
        files.extend(path.glob(ext))
    
    print(f"📁 找到 {len(files)} 张图片")
    success = 0
    
    for img_file in files:
        print(f"\n处理: {img_file.name}")
        if operation == 'compress':
            if compress_image(img_file, **kwargs):
                success += 1
        elif operation == 'resize':
            if resize_image(img_file, **kwargs):
                success += 1
        elif operation == 'watermark':
            if add_watermark(img_file, **kwargs):
                success += 1
        elif operation == 'convert':
            if convert_format(img_file, **kwargs):
                success += 1
    
    print(f"\n✅ 成功: {success}/{len(files)}")

def show_info(input_file):
    """显示图片信息"""
    info = get_image_info(input_file)
    if info:
        file_size = Path(input_file).stat().st_size / 1024
        print(f"🖼️  {input_file}")
        print(f"   格式: {info['format']}")
        print(f"   模式: {info['mode']}")
        print(f"   尺寸: {info['width']}x{info['height']}")
        print(f"   大小: {file_size:.1f} KB")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(
        description='Image CLI - 图片处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  img-cli info photo.jpg                           # 查看信息
  img-cli compress photo.jpg -q 80                 # 压缩到80%质量
  img-cli resize photo.jpg -w 800                  # 调整宽度为800px
  img-cli resize photo.jpg -w 800 -H 600           # 调整为800x600
  img-cli resize photo.jpg -s 0.5                  # 缩小50%
  img-cli watermark photo.jpg "Copyright"          # 添加水印
  img-cli convert photo.jpg -f webp                # 转webp格式
  img-cli crop photo.jpg -l 100 -t 100 -r 500 -b 500  # 裁剪区域
  img-cli batch ./photos/ compress -q 75           # 批量压缩
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看图片信息')
    info_parser.add_argument('input', help='输入图片')
    
    # compress 命令
    compress_parser = subparsers.add_parser('compress', help='压缩图片')
    compress_parser.add_argument('input', help='输入图片')
    compress_parser.add_argument('-o', '--output', help='输出文件')
    compress_parser.add_argument('-q', '--quality', type=int, default=85, help='JPEG质量 1-100 (默认: 85)')
    compress_parser.add_argument('-m', '--max-size', type=int, help='最大边长像素')
    
    # resize 命令
    resize_parser = subparsers.add_parser('resize', help='调整大小')
    resize_parser.add_argument('input', help='输入图片')
    resize_parser.add_argument('-o', '--output', help='输出文件')
    resize_parser.add_argument('-w', '--width', type=int, help='目标宽度')
    resize_parser.add_argument('-H', '--height', type=int, help='目标高度')
    resize_parser.add_argument('-s', '--scale', type=float, help='缩放比例 (如 0.5)')
    
    # watermark 命令
    watermark_parser = subparsers.add_parser('watermark', help='添加水印')
    watermark_parser.add_argument('input', help='输入图片')
    watermark_parser.add_argument('text', help='水印文字')
    watermark_parser.add_argument('-o', '--output', help='输出文件')
    watermark_parser.add_argument('-p', '--position', choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                                  default='bottom-right', help='水印位置')
    watermark_parser.add_argument('--opacity', type=int, default=128, help='透明度 0-255 (默认: 128)')
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='格式转换')
    convert_parser.add_argument('input', help='输入图片')
    convert_parser.add_argument('-o', '--output', help='输出文件')
    convert_parser.add_argument('-f', '--format', choices=['jpg', 'png', 'webp', 'gif', 'bmp', 'tiff'],
                                help='目标格式')
    
    # crop 命令
    crop_parser = subparsers.add_parser('crop', help='裁剪图片')
    crop_parser.add_argument('input', help='输入图片')
    crop_parser.add_argument('-o', '--output', help='输出文件')
    crop_parser.add_argument('-l', '--left', type=int, default=0, help='左边界')
    crop_parser.add_argument('-t', '--top', type=int, default=0, help='上边界')
    crop_parser.add_argument('-r', '--right', type=int, help='右边界')
    crop_parser.add_argument('-b', '--bottom', type=int, help='下边界')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量处理')
    batch_parser.add_argument('directory', help='目标目录')
    batch_parser.add_argument('operation', choices=['compress', 'resize', 'watermark', 'convert'],
                              help='操作类型')
    batch_parser.add_argument('--quality', type=int, default=85)
    batch_parser.add_argument('--width', type=int)
    batch_parser.add_argument('--height', type=int)
    batch_parser.add_argument('--text', help='水印文字')
    batch_parser.add_argument('--format', help='目标格式')
    
    args = parser.parse_args()
    
    if args.command == 'info':
        show_info(args.input)
    elif args.command == 'compress':
        compress_image(args.input, args.output, args.quality, args.max_size)
    elif args.command == 'resize':
        resize_image(args.input, args.output, args.width, args.height, args.scale)
    elif args.command == 'watermark':
        add_watermark(args.input, args.text, args.output, args.position, args.opacity)
    elif args.command == 'convert':
        convert_format(args.input, args.output, args.format)
    elif args.command == 'crop':
        crop_image(args.input, args.output, args.left, args.top, args.right, args.bottom)
    elif args.command == 'batch':
        kwargs = {}
        if args.quality: kwargs['quality'] = args.quality
        if args.width: kwargs['width'] = args.width
        if args.height: kwargs['height'] = args.height
        if args.text: kwargs['text'] = args.text
        if args.format: kwargs['format'] = args.format
        batch_process(args.directory, args.operation, **kwargs)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
