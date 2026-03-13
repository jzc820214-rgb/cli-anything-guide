# CLI-Anything Agent 配置手册

> **版本**: v1.0  
> **创建时间**: 2026-03-13  
> **适用对象**: nanobot Agent  
> **用途**: 快速将任意软件转换为 CLI 工具

---

## 1. 概述

### 1.1 什么是 CLI-Anything

CLI-Anything 是 HKUDS 实验室开发的一套方法论和工具集，用于将任何软件（有源代码的）转换为 AI Agent 可使用的命令行工具。

**核心思想**:
- CLI 是人类和 AI 的通用接口
- 通过自动化流程为软件生成标准化 CLI
- 使 AI Agent 能够调用专业软件完成复杂任务

### 1.2 适用场景

| 场景 | 示例 |
|------|------|
| 文档处理 | LibreOffice → 自动转 PDF、合并文档 |
| 媒体处理 | FFmpeg → 视频压缩、格式转换 |
| 图像处理 | GIMP/PIL → 批量处理、加水印 |
| 知识管理 | Zotero/自定义 → 保存、搜索、导出 |
| 图表生成 | Mermaid/Graphviz → 流程图、架构图 |

### 1.3 技术原理

```
软件源码/可执行文件
       ↓
[CLI-Anything 分析层]
   - 扫描功能接口
   - 映射 GUI 到命令行
   - 设计命令结构
       ↓
[CLI 生成层]
   - 生成 Python/Click 代码
   - 实现 REPL 交互
   - JSON 输出支持
       ↓
[安装层]
   - pip install -e .
   - 注册到 PATH
       ↓
可用 CLI 工具
```

---

## 2. 前置要求

### 2.1 系统环境

```bash
# 检查 Python
python3 --version  # 要求 >= 3.8

# 检查 pip
pip3 --version

# 检查基础工具
which git
which curl
```

### 2.2 安装依赖

```bash
# 1. 安装 Pillow（图像处理）
pip3 install Pillow

# 2. 安装 pypdf（PDF 处理）
pip3 install pypdf

# 3. 安装其他常用库
pip3 install click requests
```

### 2.3 创建工作目录

```bash
# 创建 CLI 工具目录
mkdir -p ~/.nanobot/workspace/cli-tools
mkdir -p ~/.local/bin

# 添加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## 3. CLI 工具创建规范

### 3.1 标准结构

每个 CLI 工具应遵循以下结构：

```
cli-{name}/
├── cli-{name}.py      # 主入口文件
├── README.md          # 使用说明
└── setup.py           # 安装配置（可选）
```

### 3.2 代码模板

```python
#!/usr/bin/env python3
"""
{Tool} CLI - {简要描述}
功能: {功能1}, {功能2}, {功能3}
"""
import argparse
import sys
from pathlib import Path

# 配置参数
DEFAULT_OUTPUT_DIR = Path("/home/jw/.nanobot/workspace/output")


def function_one(args):
    """功能一实现"""
    print(f"✅ 功能一完成: {args}")
    return True


def function_two(args):
    """功能二实现"""
    print(f"✅ 功能二完成: {args}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='{Tool} CLI - {描述}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  cli-{name} cmd1 arg1                    # 示例1
  cli-{name} cmd2 arg2 --option          # 示例2
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 命令1
    cmd1_parser = subparsers.add_parser('cmd1', help='功能1说明')
    cmd1_parser.add_argument('arg', help='参数说明')
    cmd1_parser.add_argument('-o', '--output', help='输出文件')
    
    # 命令2
    cmd2_parser = subparsers.add_parser('cmd2', help='功能2说明')
    cmd2_parser.add_argument('arg', help='参数说明')
    
    args = parser.parse_args()
    
    if args.command == 'cmd1':
        function_one(args)
    elif args.command == 'cmd2':
        function_two(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
```

### 3.3 安装规范

```bash
# 1. 创建软链接到 PATH
chmod +x /path/to/cli-name.py
ln -sf /path/to/cli-name.py ~/.local/bin/cli-name

# 2. 验证安装
cli-name --help

# 3. 记录到工具清单
echo "cli-name - 功能描述" >> ~/.nanobot/workspace/cli-tools/TOOLS.md
```

---

## 4. 现有工具清单

### 4.1 已部署工具

| 工具名 | 命令 | 功能 | 文件位置 |
|--------|------|------|----------|
| LibreOffice CLI | `lo-cli` | 文档转PDF、合并、提取文本 | `~/.nanobot/workspace/lo-cli.py` |
| FFmpeg CLI | `ffmpeg-cli` | 视频压缩、GIF、音频提取 | `~/.nanobot/workspace/ffmpeg-cli.py` |
| Image CLI | `img-cli` | 图片压缩、水印、格式转换 | `~/.nanobot/workspace/img-cli.py` |
| Knowledge Base CLI | `kb-cli` | 知识管理、搜索、导出 | `~/.nanobot/workspace/kb-cli.py` |
| Diagram CLI | `diagram-cli` | 流程图、架构图生成 | `~/.nanobot/workspace/diagram-cli.py` |

### 4.2 工具状态检查

```bash
# 检查所有工具是否可用
check_cli_tools() {
    tools=("lo-cli" "ffmpeg-cli" "img-cli" "kb-cli" "diagram-cli")
    for tool in "${tools[@]}"; do
        if command -v $tool &>/dev/null; then
            echo "✅ $tool 已安装"
        else
            echo "❌ $tool 未安装"
        fi
    done
}

check_cli_tools
```

---

## 5. 新工具创建流程

### 5.1 需求分析

1. **确定目标软件**
   - 是否有命令行接口？
   - 是否需要 GUI 自动化？
   - 输出格式是什么？

2. **定义核心功能**
   - 最常用的 3-5 个功能
   - 输入输出格式
   - 是否需要批处理

### 5.2 实现步骤

```bash
# Step 1: 创建文件
TOOL_NAME="my-tool"
FILE="~/.nanobot/workspace/${TOOL_NAME}-cli.py"

# Step 2: 使用模板生成代码
# (复制第3.2节的模板并修改)

# Step 3: 添加执行权限
chmod +x $FILE

# Step 4: 创建软链接
ln -sf $FILE ~/.local/bin/${TOOL_NAME}-cli

# Step 5: 测试
${TOOL_NAME}-cli --help
```

### 5.3 功能测试清单

- [ ] 基本命令可以运行
- [ ] 所有子命令可用
- [ ] 错误处理正常
- [ ] 输出格式正确
- [ ] 批处理功能正常（如有）

---

## 6. 与 nanobot 集成

### 6.1 自动调用场景

```python
# 在 daily-learn.sh 中自动使用示例

# 1. 生成 PDF 报告
if command -v lo-cli &>/dev/null; then
    lo-cli convert report.txt -o report.pdf
fi

# 2. 保存到知识库
if command -v kb-cli &>/dev/null; then
    kb-cli add "标题" "内容" -t "tag1,tag2"
fi

# 3. 生成图表
if command -v diagram-cli &>/dev/null; then
    diagram-cli flow "流程名" "步骤1" "步骤2" "步骤3"
fi
```

### 6.2 响应用户指令

当用户有以下需求时，主动使用对应工具：

| 用户需求 | 使用工具 | 命令示例 |
|---------|---------|---------|
| "转PDF" | lo-cli | `lo-cli convert file.docx` |
| "压缩视频" | ffmpeg-cli | `ffmpeg-cli compress video.mp4` |
| "压缩图片" | img-cli | `img-cli compress photo.jpg` |
| "保存这个" | kb-cli | `kb-cli add "标题" "内容"` |
| "画流程图" | diagram-cli | `diagram-cli flow ...` |

---

## 7. 最佳实践

### 7.1 代码规范

- 使用 `argparse` 处理命令行参数
- 所有输出使用 UTF-8 编码
- 错误信息使用 `❌` 前缀
- 成功信息使用 `✅` 前缀
- 提示信息使用 `ℹ️` 或 `⚠️` 前缀

### 7.2 错误处理

```python
def safe_execute(func, *args, **kwargs):
    """安全执行函数"""
    try:
        return func(*args, **kwargs)
    except FileNotFoundError:
        print(f"❌ 文件不存在")
        return False
    except PermissionError:
        print(f"❌ 权限不足")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)[:100]}")
        return False
```

### 7.3 性能优化

- 大文件处理使用流式读写
- 批处理添加进度提示
- 设置合理的超时时间
- 避免重复加载库

---

## 8. 故障排除

### 8.1 常见问题

**Q: 命令未找到**
```bash
# 检查软链接
ls -la ~/.local/bin/cli-name

# 检查 PATH
echo $PATH | grep ".local/bin"

# 重新创建链接
ln -sf /path/to/cli.py ~/.local/bin/cli-name
```

**Q: 依赖缺失**
```bash
# 检查 Python 版本
python3 --version

# 安装缺失依赖
pip3 install package-name
```

**Q: 权限错误**
```bash
# 添加执行权限
chmod +x /path/to/cli.py

# 检查文件所有者
ls -la /path/to/cli.py
```

### 8.2 调试模式

```bash
# 启用详细输出
cli-name command --verbose

# 查看 Python 错误
python3 -m pdb /path/to/cli.py command
```

---

## 9. 扩展开发

### 9.1 添加新功能

1. 在主文件中添加新函数
2. 在 `argparse` 中添加新子命令
3. 更新帮助文档 (`epilog`)
4. 测试并更新版本号

### 9.2 集成外部 API

```python
import requests

def api_call(endpoint, data):
    """调用外部 API"""
    try:
        response = requests.post(endpoint, json=data, timeout=30)
        return response.json()
    except requests.RequestException as e:
        print(f"❌ API 调用失败: {e}")
        return None
```

---

## 10. 参考资源

### 10.1 官方资源

- CLI-Anything GitHub: https://github.com/HKUDS/CLI-Anything
- Mermaid 文档: https://mermaid.js.org/
- Graphviz 文档: https://graphviz.org/

### 10.2 内部文档

- 工具源码: `~/.nanobot/workspace/*-cli.py`
- 知识库数据: `~/.nanobot/workspace/knowledge-base/`
- 生成图表: `~/.nanobot/workspace/diagrams/`
- PDF 存档: `~/.nanobot/workspace/skills/self-evolution/.learnings/pdfs/`

---

## 附录 A: 快速参考卡

```bash
# LibreOffice
lo-cli convert file.docx              # 转 PDF
lo-cli merge out.pdf a.pdf b.pdf      # 合并 PDF

# FFmpeg
ffmpeg-cli compress video.mp4         # 压缩视频
ffmpeg-cli gif video.mp4              # 转 GIF
ffmpeg-cli audio video.mp4            # 提取音频
ffmpeg-cli cut video.mp4 00:01:00 30  # 裁剪

# Image
img-cli compress photo.jpg -q 80      # 压缩图片
img-cli resize photo.jpg -w 800       # 调整大小
img-cli watermark photo.jpg "Text"    # 加水印
img-cli convert photo.jpg -f webp     # 格式转换

# Knowledge Base
kb-cli add "标题" "内容" -t "tag"     # 添加条目
kb-cli search "关键词"                # 搜索
kb-cli list                           # 列出所有
kb-cli export -o kb.md                # 导出

# Diagram
diagram-cli flow "标题" A B C         # 流程图
diagram-cli arch "标题" 层1 层2 层3    # 架构图
diagram-cli sequence --actors A,B --steps "A,B,msg"  # 时序图
```

---

**文档结束**  
*上次更新: 2026-03-13*  
*维护者: nanobot Agent*
