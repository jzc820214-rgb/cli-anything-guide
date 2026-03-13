#!/usr/bin/env python3
"""
LibreOffice CLI - 简化版命令行工具
功能：文档转PDF、批量处理、创建简单文档
"""
import subprocess
import argparse
import sys
import os
from pathlib import Path

def convert_to_pdf(input_file, output_file=None):
    """将文档转为 PDF"""
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')
    
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', str(Path(output_file).parent),
        str(input_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ 转换成功: {input_file} → {output_file}")
            return True
        else:
            print(f"❌ 转换失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def batch_convert(directory, pattern="*"):
    """批量转换目录中的文档"""
    path = Path(directory)
    if not path.exists():
        print(f"❌ 目录不存在: {directory}")
        return
    
    files = list(path.glob(pattern))
    supported = ['.docx', '.doc', '.odt', '.txt', '.rtf']
    to_convert = [f for f in files if f.suffix.lower() in supported]
    
    print(f"📁 找到 {len(to_convert)} 个可转换文件")
    success = 0
    for f in to_convert:
        if convert_to_pdf(f):
            success += 1
    
    print(f"\n✅ 成功: {success}/{len(to_convert)}")

def merge_pdfs(output, *input_files):
    """合并多个 PDF（使用 pypdf，无需外部依赖）"""
    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        print("📦 需要安装 pypdf，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pypdf', '-q'], 
                      capture_output=True)
        from pypdf import PdfWriter, PdfReader
    
    if not input_files:
        print("❌ 请提供至少一个输入文件")
        return
    
    writer = PdfWriter()
    total_pages = 0
    for pdf in input_files:
        if Path(pdf).exists():
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)
            total_pages += len(reader.pages)
            print(f"  添加: {pdf} ({len(reader.pages)} 页)")
        else:
            print(f"  ⚠️  跳过: {pdf} (不存在)")
    
    with open(output, 'wb') as f:
        writer.write(f)
    print(f"✅ 合并成功: {output} (共 {total_pages} 页)")

def extract_text(pdf_file, output=None):
    """从 PDF 提取文本"""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("❌ 需要安装 pypdf: pip install pypdf")
        return
    
    if not Path(pdf_file).exists():
        print(f"❌ 文件不存在: {pdf_file}")
        return
    
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- 第 {i+1} 页 ---\n{page_text}"
        
        if output:
            Path(output).write_text(text, encoding='utf-8')
            print(f"✅ 文本已保存: {output}")
        else:
            print(text)
        return True
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        return False

def pdf_info(pdf_file):
    """显示 PDF 信息"""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("❌ 需要安装 pypdf: pip install pypdf")
        return
    
    if not Path(pdf_file).exists():
        print(f"❌ 文件不存在: {pdf_file}")
        return
    
    try:
        reader = PdfReader(pdf_file)
        print(f"📄 {pdf_file}")
        print(f"   页数: {len(reader.pages)}")
        print(f"   大小: {Path(pdf_file).stat().st_size / 1024:.1f} KB")
        if reader.metadata:
            print(f"   标题: {reader.metadata.get('/Title', 'N/A')}")
            print(f"   作者: {reader.metadata.get('/Author', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='LibreOffice CLI - 文档处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s convert document.docx              # 转为 PDF
  %(prog)s batch ./documents/                # 批量转换
  %(prog)s batch ./documents/ "*.docx"       # 批量转换 docx 文件
  %(prog)s merge output.pdf a.pdf b.pdf      # 合并 PDF
  %(prog)s extract document.pdf -o text.txt  # 提取文本
  %(prog)s info document.pdf                 # 查看 PDF 信息
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='文档转 PDF')
    convert_parser.add_argument('input', help='输入文件')
    convert_parser.add_argument('-o', '--output', help='输出文件（默认同名.pdf）')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量转换')
    batch_parser.add_argument('directory', help='目标目录')
    batch_parser.add_argument('pattern', nargs='?', default="*", 
                              help='文件匹配模式（默认*）')
    
    # merge 命令
    merge_parser = subparsers.add_parser('merge', help='合并 PDF')
    merge_parser.add_argument('output', help='输出文件')
    merge_parser.add_argument('inputs', nargs='+', help='输入文件')
    
    # extract 命令
    extract_parser = subparsers.add_parser('extract', help='从 PDF 提取文本')
    extract_parser.add_argument('input', help='输入 PDF 文件')
    extract_parser.add_argument('-o', '--output', help='输出文本文件（默认输出到屏幕）')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='显示 PDF 信息')
    info_parser.add_argument('input', help='输入 PDF 文件')
    
    args = parser.parse_args()
    
    if args.command == 'convert':
        convert_to_pdf(args.input, args.output)
    elif args.command == 'batch':
        batch_convert(args.directory, args.pattern)
    elif args.command == 'merge':
        merge_pdfs(args.output, *args.inputs)
    elif args.command == 'extract':
        extract_text(args.input, args.output)
    elif args.command == 'info':
        pdf_info(args.input)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
