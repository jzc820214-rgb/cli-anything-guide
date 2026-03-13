#!/usr/bin/env python3
"""
Diagram CLI - 图表生成工具
功能：生成流程图、架构图、思维导图
支持格式：Mermaid、Graphviz、PlantUML
"""
import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

DIAGRAM_DIR = Path("/home/jw/.nanobot/workspace/diagrams")
DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)

def generate_flowchart(nodes, edges, direction="TB"):
    """生成流程图 (Mermaid)"""
    lines = [f"flowchart {direction}"]
    
    # 添加节点
    for node_id, node_text in nodes.items():
        lines.append(f"    {node_id}[{node_text}]")
    
    # 添加连接
    for edge in edges:
        if len(edge) == 2:
            from_node, to_node = edge
            lines.append(f"    {from_node} --> {to_node}")
        elif len(edge) == 3:
            from_node, to_node, label = edge
            lines.append(f"    {from_node} -->|{label}| {to_node}")
    
    return "\n".join(lines)

def generate_sequence(actors, steps):
    """生成时序图 (Mermaid)"""
    lines = ["sequenceDiagram"]
    
    # 添加参与者
    for actor in actors:
        lines.append(f"    participant {actor}")
    
    # 添加步骤
    for step in steps:
        if len(step) == 2:
            from_actor, to_actor = step
            lines.append(f"    {from_actor}->>{to_actor}: message")
        elif len(step) == 3:
            from_actor, to_actor, message = step
            lines.append(f"    {from_actor}->>{to_actor}: {message}")
    
    return "\n".join(lines)

def generate_mindmap(center, branches):
    """生成思维导图 (Mermaid)"""
    lines = ["mindmap"]
    lines.append(f"  root(({center}))")
    
    for branch, leaves in branches.items():
        lines.append(f"    {branch}")
        if isinstance(leaves, list):
            for leaf in leaves:
                lines.append(f"      {leaf}")
        elif isinstance(leaves, dict):
            for sub_branch, sub_leaves in leaves.items():
                lines.append(f"      {sub_branch}")
                for sub_leaf in sub_leaves:
                    lines.append(f"        {sub_leaf}")
    
    return "\n".join(lines)

def generate_architecture(components, connections):
    """生成架构图 (Graphviz)"""
    lines = [
        "digraph Architecture {",
        "    rankdir=TB;",
        "    node [shape=box, style=filled, fillcolor=lightblue];",
        "    edge [arrowhead=vee];",
        ""
    ]
    
    # 添加组件
    for comp_id, comp_info in components.items():
        if isinstance(comp_info, str):
            lines.append(f'    {comp_id} [label="{comp_info}"];')
        elif isinstance(comp_info, dict):
            label = comp_info.get('label', comp_id)
            color = comp_info.get('color', 'lightblue')
            shape = comp_info.get('shape', 'box')
            lines.append(f'    {comp_id} [label="{label}", fillcolor={color}, shape={shape}];')
    
    lines.append("")
    
    # 添加连接
    for conn in connections:
        if len(conn) == 2:
            lines.append(f"    {conn[0]} -> {conn[1]};")
        elif len(conn) == 3:
            lines.append(f'    {conn[0]} -> {conn[1]} [label="{conn[2]}"];')
    
    lines.append("}")
    return "\n".join(lines)

def generate_class_diagram(classes, relations):
    """生成类图 (Mermaid)"""
    lines = ["classDiagram"]
    
    # 添加类
    for class_name, methods in classes.items():
        lines.append(f"    class {class_name} {{")
        for method in methods:
            lines.append(f"        {method}")
        lines.append("    }")
    
    # 添加关系
    for rel in relations:
        lines.append(f"    {rel}")
    
    return "\n".join(lines)

def generate_er_diagram(entities, relationships):
    """生成 ER 图 (Mermaid)"""
    lines = ["erDiagram"]
    
    # 添加实体
    for entity, attributes in entities.items():
        lines.append(f"    {entity} {{")
        for attr in attributes:
            lines.append(f"        {attr}")
        lines.append("    }")
    
    # 添加关系
    for rel in relationships:
        lines.append(f"    {rel}")
    
    return "\n".join(lines)

def save_diagram(content, name, fmt="mmd"):
    """保存图表文件"""
    filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{fmt}"
    filepath = DIAGRAM_DIR / filename
    filepath.write_text(content, encoding='utf-8')
    print(f"✅ 图表已保存: {filepath}")
    return filepath

def export_to_png(mmd_file, output_file=None):
    """使用 mermaid-cli 导出为图片"""
    if not output_file:
        output_file = mmd_file.with_suffix('.png')
    
    # 检查是否有 mermaid-cli
    try:
        subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
        cmd = ['mmdc', '-i', str(mmd_file), '-o', str(output_file)]
        subprocess.run(cmd, check=True)
        print(f"✅ 图片已导出: {output_file}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  mermaid-cli (mmdc) 未安装")
        print("   安装: npm install -g @mermaid-js/mermaid-cli")
        print(f"   或使用在线工具: https://mermaid.live")
        return False

def export_to_svg(dot_file, output_file=None):
    """使用 dot 导出 SVG"""
    if not output_file:
        output_file = dot_file.with_suffix('.svg')
    
    try:
        subprocess.run(['dot', '-V'], capture_output=True, check=True)
        cmd = ['dot', '-Tsvg', str(dot_file), '-o', str(output_file)]
        subprocess.run(cmd, check=True)
        print(f"✅ SVG 已导出: {output_file}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Graphviz (dot) 未安装")
        print("   安装: sudo apt install graphviz")
        return False

def list_diagrams():
    """列出所有图表"""
    files = sorted(DIAGRAM_DIR.glob('*.*'))
    
    if not files:
        print("📂 暂无图表")
        return
    
    print(f"\n📊 图表列表 ({len(files)} 个)\n")
    
    for f in files:
        size = f.stat().st_size / 1024
        date = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"  {f.name:50} {size:8.1f} KB  {date}")
    print()

def quick_flow(title, steps):
    """快速生成简单流程图"""
    nodes = {}
    edges = []
    
    for i, step in enumerate(steps):
        node_id = f"N{i}"
        nodes[node_id] = step
        if i > 0:
            edges.append((f"N{i-1}", node_id))
    
    content = generate_flowchart(nodes, edges)
    return save_diagram(content, title.replace(' ', '_'))

def quick_architecture(title, layers):
    """快速生成分层架构图"""
    components = {}
    connections = []
    
    prev_layer = None
    for i, layer in enumerate(layers):
        layer_id = f"L{i}"
        layer_name = layer if isinstance(layer, str) else layer.get('name', f'Layer{i}')
        components[layer_id] = {
            'label': layer_name,
            'color': 'lightyellow' if i == 0 else 'lightgreen' if i == len(layers)-1 else 'lightblue'
        }
        if prev_layer:
            connections.append((prev_layer, layer_id))
        prev_layer = layer_id
    
    content = generate_architecture(components, connections)
    return save_diagram(content, title.replace(' ', '_'), 'dot')

def main():
    parser = argparse.ArgumentParser(
        description='Diagram CLI - 图表生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速流程图
  diagram-cli flow "部署流程" "代码提交" "CI构建" "测试" "部署"
  
  # 快速架构图
  diagram-cli arch "系统架构" "前端" "API网关" "服务层" "数据库"
  
  # 时序图
  diagram-cli sequence "登录流程" --actors user,server,db \\
    --steps "user,server,输入凭证" "server,db,验证用户" "db,server,返回结果"
  
  # 思维导图
  diagram-cli mindmap "项目规划" --center "产品" \\
    --branch "技术:前端,后端,数据库" --branch "市场:推广,运营"
  
  # 列出所有图表
  diagram-cli list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # flow 命令 - 快速流程图
    flow_parser = subparsers.add_parser('flow', help='快速生成流程图')
    flow_parser.add_argument('title', help='图表标题')
    flow_parser.add_argument('steps', nargs='+', help='流程步骤')
    flow_parser.add_argument('-d', '--direction', default='TB', 
                             choices=['TB', 'BT', 'LR', 'RL'],
                             help='方向 (默认: TB)')
    
    # arch 命令 - 快速架构图
    arch_parser = subparsers.add_parser('arch', help='快速生成架构图')
    arch_parser.add_argument('title', help='图表标题')
    arch_parser.add_argument('layers', nargs='+', help='架构层次')
    
    # sequence 命令 - 时序图
    seq_parser = subparsers.add_parser('sequence', help='生成时序图')
    seq_parser.add_argument('title', help='图表标题')
    seq_parser.add_argument('--actors', required=True, help='参与者（逗号分隔）')
    seq_parser.add_argument('--steps', nargs='+', required=True, 
                            help='步骤: from,to,message')
    
    # mindmap 命令 - 思维导图
    mind_parser = subparsers.add_parser('mindmap', help='生成思维导图')
    mind_parser.add_argument('title', help='图表标题')
    mind_parser.add_argument('--center', required=True, help='中心主题')
    mind_parser.add_argument('--branch', nargs='+', required=True,
                            help='分支: 名称:子项1,子项2')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有图表')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出图表为图片')
    export_parser.add_argument('file', help='图表文件路径')
    export_parser.add_argument('-f', '--format', choices=['png', 'svg', 'pdf'],
                               default='png', help='输出格式')
    export_parser.add_argument('-o', '--output', help='输出文件')
    
    args = parser.parse_args()
    
    if args.command == 'flow':
        quick_flow(args.title, args.steps)
    elif args.command == 'arch':
        quick_architecture(args.title, args.layers)
    elif args.command == 'sequence':
        actors = args.actors.split(',')
        steps = []
        for step in args.steps:
            parts = step.split(',')
            steps.append(parts)
        content = generate_sequence(actors, steps)
        save_diagram(content, args.title.replace(' ', '_'))
    elif args.command == 'mindmap':
        branches = {}
        for branch_str in args.branch:
            if ':' in branch_str:
                name, items = branch_str.split(':', 1)
                branches[name] = items.split(',')
        content = generate_mindmap(args.center, branches)
        save_diagram(content, args.title.replace(' ', '_'))
    elif args.command == 'list':
        list_diagrams()
    elif args.command == 'export':
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"❌ 文件不存在: {args.file}")
            return
        if filepath.suffix == '.mmd':
            export_to_png(filepath, args.output)
        elif filepath.suffix == '.dot':
            export_to_svg(filepath, args.output)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
