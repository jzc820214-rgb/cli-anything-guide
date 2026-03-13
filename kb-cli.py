#!/usr/bin/env python3
"""
Knowledge Base CLI - 知识库管理工具
功能：保存内容、添加标签、搜索、导出
"""
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib
import re

KB_DIR = Path("/home/jw/.nanobot/workspace/knowledge-base")
KB_FILE = KB_DIR / "database.json"

def init_kb():
    """初始化知识库"""
    KB_DIR.mkdir(parents=True, exist_ok=True)
    if not KB_FILE.exists():
        KB_FILE.write_text(json.dumps({"entries": [], "tags": []}, indent=2))

def load_kb():
    """加载知识库"""
    init_kb()
    return json.loads(KB_FILE.read_text())

def save_kb(data):
    """保存知识库"""
    KB_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def generate_id(content):
    """生成条目 ID"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def add_entry(title, content, source=None, tags=None):
    """添加知识条目"""
    kb = load_kb()
    
    entry = {
        "id": generate_id(title + content),
        "title": title,
        "content": content,
        "source": source or "",
        "tags": tags or [],
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    
    # 检查是否已存在
    for existing in kb["entries"]:
        if existing["id"] == entry["id"]:
            print(f"⚠️  条目已存在: {existing['id']}")
            return False
    
    kb["entries"].insert(0, entry)  # 新条目在前
    
    # 更新标签列表
    for tag in (tags or []):
        if tag not in kb["tags"]:
            kb["tags"].append(tag)
    
    save_kb(kb)
    print(f"✅ 已添加: [{entry['id']}] {title}")
    return True

def list_entries(tag=None, limit=20):
    """列岀条目"""
    kb = load_kb()
    entries = kb["entries"]
    
    if tag:
        entries = [e for e in entries if tag in e.get("tags", [])]
    
    print(f"\n📚 知识库 ({len(entries)} 条{'，标签: ' + tag if tag else ''})\n")
    
    for i, entry in enumerate(entries[:limit], 1):
        date = entry["created"][:10]
        tags = " ".join([f"#{t}" for t in entry.get("tags", [])])
        source = f" | {entry['source'][:30]}..." if entry.get("source") else ""
        print(f"{i}. [{entry['id']}] {entry['title']}")
        print(f"   📅 {date} {tags}{source}\n")
    
    if len(entries) > limit:
        print(f"... 还有 {len(entries) - limit} 条")

def search_entries(keyword):
    """搜索条目"""
    kb = load_kb()
    results = []
    
    keyword_lower = keyword.lower()
    for entry in kb["entries"]:
        if (keyword_lower in entry["title"].lower() or 
            keyword_lower in entry["content"].lower() or
            keyword_lower in " ".join(entry.get("tags", [])).lower()):
            results.append(entry)
    
    print(f"\n🔍 搜索 '{keyword}' 找到 {len(results)} 条结果\n")
    
    for entry in results[:20]:
        date = entry["created"][:10]
        tags = " ".join([f"#{t}" for t in entry.get("tags", [])])
        content_preview = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
        print(f"[{entry['id']}] {entry['title']}")
        print(f"  📅 {date} {tags}")
        print(f"  📝 {content_preview}\n")

def show_entry(entry_id):
    """显示单条条目详情"""
    kb = load_kb()
    
    for entry in kb["entries"]:
        if entry["id"] == entry_id:
            print(f"\n📄 {entry['title']}")
            print(f"   ID: {entry['id']}")
            print(f"   创建: {entry['created']}")
            print(f"   更新: {entry['updated']}")
            print(f"   标签: {' '.join(['#' + t for t in entry.get('tags', [])])}")
            print(f"   来源: {entry.get('source', 'N/A')}")
            print(f"\n{entry['content']}\n")
            return
    
    print(f"❌ 未找到条目: {entry_id}")

def delete_entry(entry_id):
    """删除条目"""
    kb = load_kb()
    
    original_len = len(kb["entries"])
    kb["entries"] = [e for e in kb["entries"] if e["id"] != entry_id]
    
    if len(kb["entries"]) < original_len:
        save_kb(kb)
        print(f"✅ 已删除: {entry_id}")
        return True
    else:
        print(f"❌ 未找到条目: {entry_id}")
        return False

def list_tags():
    """列岀所有标签"""
    kb = load_kb()
    tags = kb.get("tags", [])
    
    print(f"\n🏷️  标签列表 ({len(tags)} 个)\n")
    
    # 统计每个标签的条目数
    tag_counts = {}
    for entry in kb["entries"]:
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    for tag in sorted(tags):
        count = tag_counts.get(tag, 0)
        print(f"  #{tag} ({count} 条)")
    print()

def export_entries(format="markdown", output=None):
    """导出条目"""
    kb = load_kb()
    
    if format == "markdown":
        lines = ["# 知识库导出\n", f"生成时间: {datetime.now().isoformat()}\n", f"条目数: {len(kb['entries'])}\n\n---\n"]
        
        for entry in kb["entries"]:
            lines.append(f"\n## {entry['title']}\n")
            lines.append(f"**ID**: {entry['id']}  ")
            lines.append(f"**创建**: {entry['created'][:10]}  ")
            lines.append(f"**标签**: {' '.join(['#' + t for t in entry.get('tags', [])])}  ")
            if entry.get("source"):
                lines.append(f"**来源**: {entry['source']}  ")
            lines.append(f"\n{entry['content']}\n")
            lines.append("---\n")
        
        content = "".join(lines)
        
    elif format == "json":
        content = json.dumps(kb, indent=2, ensure_ascii=False)
    
    if output:
        Path(output).write_text(content, encoding='utf-8')
        print(f"✅ 已导出到: {output}")
    else:
        print(content)

def import_url(url, title=None):
    """从 URL 导入（简化版，仅保存链接）"""
    if not title:
        title = url
    
    add_entry(
        title=title,
        content=f"链接: {url}",
        source=url,
        tags=["imported", "url"]
    )

def show_stats():
    """显示统计信息"""
    kb = load_kb()
    entries = kb["entries"]
    tags = kb.get("tags", [])
    
    print(f"\n📊 知识库统计\n")
    print(f"  总条目: {len(entries)}")
    print(f"  总标签: {len(tags)}")
    
    # 本月新增
    this_month = datetime.now().strftime("%Y-%m")
    month_count = sum(1 for e in entries if e["created"].startswith(this_month))
    print(f"  本月新增: {month_count}")
    
    # 来源统计
    sources = {}
    for e in entries:
        src = e.get("source", "")
        if src:
            domain = re.search(r'https?://([^/]+)', src)
            if domain:
                sources[domain.group(1)] = sources.get(domain.group(1), 0) + 1
    
    if sources:
        print(f"\n  主要来源:")
        for domain, count in sorted(sources.items(), key=lambda x: -x[1])[:5]:
            print(f"    - {domain}: {count} 条")
    print()

def main():
    parser = argparse.ArgumentParser(
        description='Knowledge Base CLI - 知识库管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  kb-cli add "文章标题" "内容..." -t "tag1,tag2"     # 添加条目
  kb-cli add "文章标题" "内容..." -s "https://..."     # 添加带来源
  kb-cli list                                          # 列出条目
  kb-cli list -t "python"                              # 按标签筛选
  kb-cli search "关键词"                               # 搜索
  kb-cli show abc123                                   # 查看详情
  kb-cli delete abc123                                 # 删除条目
  kb-cli tags                                          # 列出标签
  kb-cli stats                                         # 统计信息
  kb-cli export -f markdown -o kb.md                   # 导出 Markdown
  kb-cli import-url "https://..." "标题"               # 导入链接
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加条目')
    add_parser.add_argument('title', help='标题')
    add_parser.add_argument('content', help='内容')
    add_parser.add_argument('-s', '--source', help='来源 URL')
    add_parser.add_argument('-t', '--tags', help='标签（逗号分隔）')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列岀条目')
    list_parser.add_argument('-t', '--tag', help='按标签筛选')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='显示数量')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索条目')
    search_parser.add_argument('keyword', help='关键词')
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='显示详情')
    show_parser.add_argument('id', help='条目 ID')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除条目')
    delete_parser.add_argument('id', help='条目 ID')
    
    # tags 命令
    subparsers.add_parser('tags', help='列岀标签')
    
    # stats 命令
    subparsers.add_parser('stats', help='统计信息')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出条目')
    export_parser.add_argument('-f', '--format', choices=['markdown', 'json'], 
                               default='markdown', help='导出格式')
    export_parser.add_argument('-o', '--output', help='输出文件')
    
    # import-url 命令
    import_parser = subparsers.add_parser('import-url', help='导入链接')
    import_parser.add_argument('url', help='URL')
    import_parser.add_argument('title', nargs='?', help='标题')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        tags = args.tags.split(',') if args.tags else []
        add_entry(args.title, args.content, args.source, tags)
    elif args.command == 'list':
        list_entries(args.tag, args.limit)
    elif args.command == 'search':
        search_entries(args.keyword)
    elif args.command == 'show':
        show_entry(args.id)
    elif args.command == 'delete':
        delete_entry(args.id)
    elif args.command == 'tags':
        list_tags()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'export':
        export_entries(args.format, args.output)
    elif args.command == 'import-url':
        import_url(args.url, args.title)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
