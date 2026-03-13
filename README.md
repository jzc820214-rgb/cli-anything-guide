# CLI-Anything Agent 配置手册

[![GitHub](https://img.shields.io/badge/GitHub-jzc820214--rgb-blue)](https://github.com/jzc820214-rgb)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> 完整的 CLI-Anything 配置方案和详细过程指导，用于将任意软件转换为 AI Agent 可使用的命令行工具。

## 📖 文档

- [完整配置手册](./CLI-ANYTHING-AGENT-GUIDE.md) - 详细的配置指南和最佳实践

## 🛠️ 包含的工具

| 工具 | 文件名 | 功能 |
|------|--------|------|
| **LibreOffice CLI** | `lo-cli.py` | 文档转 PDF、合并、提取文本 |
| **FFmpeg CLI** | `ffmpeg-cli.py` | 视频压缩、GIF、音频提取、裁剪 |
| **Image CLI** | `img-cli.py` | 图片压缩、调整大小、水印、格式转换 |
| **Knowledge Base CLI** | `kb-cli.py` | 知识库管理、标签、搜索、导出 |
| **Diagram CLI** | `diagram-cli.py` | 流程图、架构图、时序图、思维导图 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/jzc820214-rgb/cli-anything-guide.git
cd cli-anything-guide

# 创建软链接到 PATH
chmod +x *.py
ln -sf $(pwd)/lo-cli.py ~/.local/bin/lo-cli
ln -sf $(pwd)/ffmpeg-cli.py ~/.local/bin/ffmpeg-cli
ln -sf $(pwd)/img-cli.py ~/.local/bin/img-cli
ln -sf $(pwd)/kb-cli.py ~/.local/bin/kb-cli
ln -sf $(pwd)/diagram-cli.py ~/.local/bin/diagram-cli
```

### 使用示例

```bash
# 文档处理
lo-cli convert document.docx

# 视频压缩
ffmpeg-cli compress video.mp4 -q medium

# 图片处理
img-cli compress photo.jpg -q 80

# 知识管理
kb-cli add "标题" "内容" -t "tag1,tag2"

# 生成图表
diagram-cli flow "部署流程" "代码提交" "CI构建" "部署"
```

## 📦 依赖

- Python 3.8+
- Pillow (图像处理)
- pypdf (PDF 处理)
- 可选: LibreOffice, FFmpeg, Graphviz

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件

## 🙏 致谢

- [CLI-Anything](https://github.com/HKUDS/CLI-Anything) - HKUDS 实验室的原始项目
- [nanobot](https://github.com/HKUDS/nanobot) - AI Agent 框架

---

*Created by nanobot Agent on 2026-03-13*
