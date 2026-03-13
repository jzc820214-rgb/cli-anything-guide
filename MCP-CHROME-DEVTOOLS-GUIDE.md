# MCP Chrome DevTools 配置手册

> **版本**: v1.0  
> **创建时间**: 2026-03-13  
> **适用对象**: nanobot Agent + Chrome DevTools MCP

---

## 1. 概述

### 1.1 什么是 MCP

MCP (Model Context Protocol) 是 Anthropic 推出的开放协议，用于标准化 AI 助手与外部工具的通信。

### 1.2 Chrome DevTools MCP 功能

| 功能类别 | 具体能力 |
|---------|---------|
| **导航控制** | 访问网页、前进后退、刷新 |
| **DOM 操作** | 点击元素、输入文字、滚动页面、选择器查询 |
| **截图** | 全页截图、元素截图 |
| **网络监控** | 查看网络请求、拦截请求 |
| **性能分析** | 录制性能追踪、Core Web Vitals 分析 |
| **调试** | 查看控制台日志、断点调试 |

### 1.3 与简化版 chrome-cli 对比

| 功能 | chrome-cli (命令行) | MCP 完整版 |
|------|-------------------|-----------|
| 截图 | ✅ | ✅ |
| 提取 DOM | ✅ | ✅ |
| **点击元素** | ❌ | ✅ |
| **输入文字** | ❌ | ✅ |
| **滚动页面** | ❌ | ✅ |
| **网络监控** | ❌ | ✅ |
| **性能分析** | ❌ | ✅ |

---

## 2. 前置要求

### 2.1 系统环境

```bash
# 检查 nanobot 版本（需支持 MCP）
nanobot --version  # >= v0.1.4

# 检查 Node.js（用于 npx）
node --version  # >= v16

# 检查 Chrome
google-chrome --version
```

### 2.2 依赖安装

```bash
# 安装 Node.js（如未安装）
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 验证 npx
npx --version
```

---

## 3. 配置步骤

### 3.1 修改 nanobot 配置

编辑 `~/.nanobot/config.json`，添加 `tools.mcp_servers` 部分：

```json
{
  "providers": {
    "moonshot": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.moonshot.cn/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "moonshot/kimi-k2.5"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "your-bot-token",
      "allowFrom": ["*"]
    }
  },
  "tools": {
    "mcp_servers": {
      "chrome-devtools": {
        "command": "npx",
        "args": ["-y", "chrome-devtools-mcp@latest", "--headless"],
        "env": {},
        "tool_timeout": 60
      }
    }
  }
}
```

### 3.2 配置参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `command` | 启动命令 | `npx` |
| `args` | 命令参数 | 见上方 |
| `--headless` | 无头模式（不显示 GUI） | 推荐开启 |
| `--slim` | 精简模式（仅基础功能） | 可选 |
| `tool_timeout` | 工具调用超时（秒） | 60 |

### 3.3 高级配置选项

```json
{
  "tools": {
    "mcp_servers": {
      "chrome-devtools": {
        "command": "npx",
        "args": [
          "-y", 
          "chrome-devtools-mcp@latest",
          "--headless",
          "--viewport", "1920x1080",
          "--no-performance-crux",
          "--no-usage-statistics"
        ],
        "env": {
          "DEBUG": "*"
        },
        "tool_timeout": 120
      }
    }
  }
}
```

### 3.4 可选参数说明

| 参数 | 说明 |
|------|------|
| `--viewport WxH` | 设置视口大小 |
| `--no-performance-crux` | 禁用 CrUX 数据收集 |
| `--no-usage-statistics` | 禁用使用统计 |
| `--slim` | 精简模式（仅3个工具） |
| `--isolated` | 隔离用户数据目录 |

---

## 4. 启动与验证

### 4.1 重启 nanobot

**注意**: 修改配置后需要重启 gateway。

```bash
# 方法1: 手动重启
pkill -f "nanobot gateway"
nanobot gateway

# 方法2: 使用脚本（推荐）
~/.nanobot/workspace/restart-nanobot.sh
```

### 4.2 验证 MCP 工具加载

重启后，Agent 会自动调用 MCP 工具。可通过以下方式验证：

1. **导航测试**: 让 Agent 访问某个网页
2. **截图测试**: 让 Agent 截图
3. **查看日志**: 检查 `~/.nanobot/logs/gateway.log`

### 4.3 验证成功的标志

成功调用时会出现类似输出：
```
Successfully navigated to https://www.example.com.
Took a screenshot of the full current page.
```

---

## 5. 可用工具列表

### 5.1 导航类 (6个)

| 工具名 | 功能 |
|--------|------|
| `mcp_chrome_devtools_navigate_page` | 导航到指定 URL |
| `mcp_chrome_devtools_reload_page` | 刷新页面 |
| `mcp_chrome_devtools_go_back` | 后退 |
| `mcp_chrome_devtools_go_forward` | 前进 |
| `mcp_chrome_devtools_close_page` | 关闭页面 |
| `mcp_chrome_devtools_select_page` | 选择页面 |

### 5.2 输入类 (9个)

| 工具名 | 功能 |
|--------|------|
| `mcp_chrome_devtools_click` | 点击元素 |
| `mcp_chrome_devtools_type_text` | 输入文字 |
| `mcp_chrome_devtools_fill_form` | 填写表单 |
| `mcp_chrome_devtools_press_key` | 按键 |
| `mcp_chrome_devtools_hover` | 悬停 |
| `mcp_chrome_devtools_drag` | 拖拽 |
| `mcp_chrome_devtools_upload_file` | 上传文件 |
| `mcp_chrome_devtools_evaluate_script` | 执行 JS |
| `mcp_chrome_devtools_wait_for` | 等待元素 |

### 5.3 截图类 (2个)

| 工具名 | 功能 |
|--------|------|
| `mcp_chrome_devtools_take_screenshot` | 截图 |
| `mcp_chrome_devtools_take_memory_snapshot` | 内存快照 |

### 5.4 网络类 (2个)

| 工具名 | 功能 |
|--------|------|
| `mcp_chrome_devtools_list_network_requests` | 列出网络请求 |
| `mcp_chrome_devtools_get_network_request` | 获取请求详情 |

### 5.5 性能类 (4个)

| 工具名 | 功能 |
|--------|------|
| `mcp_chrome_devtools_performance_start_trace` | 开始性能追踪 |
| `mcp_chrome_devtools_performance_stop_trace` | 停止性能追踪 |
| `mcp_chrome_devtools_lighthouse_audit` | Lighthouse 审计 |
| `mcp_chrome_devtools_performance_analyze_insight` | 分析性能洞察 |

### 5.6 调试类 (6个)

| 工具名 | 功能 |
|--------|------|
| `mcp_chrome_devtools_list_console_messages` | 列出控制台消息 |
| `mcp_chrome_devtools_get_console_message` | 获取消息详情 |
| `mcp_chrome_devtools_take_snapshot` | 页面快照 |
| `mcp_chrome_devtools_emulate` | 设备模拟 |
| `mcp_chrome_devtools_resize_page` | 调整页面大小 |
| `mcp_chrome_devtools_handle_dialog` | 处理对话框 |

---

## 6. 使用示例

### 6.1 基础示例

#### 访问网页并截图
```json
// 步骤1: 导航
{
  "type": "url",
  "url": "https://www.example.com"
}

// 步骤2: 截图
{
  "fullPage": true,
  "filePath": "/tmp/screenshot.png"
}
```

#### 点击元素
```json
{
  "uid": "element-uid-from-snapshot",
  "includeSnapshot": false
}
```

#### 输入文字
```json
{
  "uid": "input-field-uid",
  "value": "搜索关键词",
  "includeSnapshot": false
}
```

### 6.2 完整工作流示例

**场景**: 在 1688 搜索商品

```
1. 导航到 1688 首页
2. 截图确认页面加载
3. 找到搜索框并点击
4. 输入商品名称
5. 点击搜索按钮
6. 等待结果加载
7. 截图查看结果
```

### 6.3 性能测试示例

```
1. 导航到目标网页
2. 开始性能追踪
3. 执行用户操作
4. 停止性能追踪
5. 生成性能报告
```

---

## 7. 故障排除

### 7.1 常见问题

#### Q: MCP 工具调用失败 (ClosedResourceError)

**原因**: MCP 服务器连接已关闭

**解决**:
```bash
# 重启 nanobot gateway
pkill -f "nanobot gateway"
nanobot gateway
```

#### Q: "The browser is already running"

**原因**: 之前的 Chrome 进程未清理

**解决**:
```bash
# 清理残留进程
pkill -9 -f "chrome-devtools-mcp"
pkill -9 -f "chrome.*remote-debugging"
rm -rf ~/.cache/chrome-devtools-mcp/chrome-profile
```

#### Q: npx 命令未找到

**原因**: Node.js 未安装或不在 PATH

**解决**:
```bash
# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 验证
npx --version
```

#### Q: Chrome 启动失败

**原因**: Chrome 未安装或权限问题

**解决**:
```bash
# 安装 Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt update
sudo apt install -y google-chrome-stable
```

### 7.2 调试方法

#### 查看 nanobot 日志
```bash
tail -f ~/.nanobot/logs/gateway.log
```

#### 手动测试 MCP 服务器
```bash
# 启动 MCP 服务器（前台运行，查看输出）
npx -y chrome-devtools-mcp@latest --headless
```

#### 检查进程状态
```bash
# 查看 nanobot
ps aux | grep nanobot

# 查看 Chrome
ps aux | grep chrome

# 查看端口占用
netstat -tulpn | grep 9222
```

### 7.3 最佳实践

1. **定期重启**: 长时间运行后建议重启 gateway
2. **清理缓存**: 每周清理 `~/.cache/chrome-devtools-mcp/`
3. **超时设置**: 根据网络情况调整 `tool_timeout`
4. **错误处理**: 调用失败时自动重试或清理进程

---

## 8. 与简化版 chrome-cli 的关系

### 8.1 功能对比

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 简单截图 | `chrome-cli` | 轻量、启动快 |
| 完整自动化 | MCP | 功能全、可交互 |
| 性能分析 | MCP | 专业工具支持 |
| 快速检查 | `chrome-cli` | 无需配置 |

### 8.2 并存使用

两个工具可以并存，根据需求选择：
- 简单任务 → `chrome-cli`
- 复杂自动化 → MCP

---

## 9. 安全注意事项

### 9.1 数据收集

Chrome DevTools MCP 默认会：
- 发送 URL 到 Google CrUX API（可禁用）
- 收集使用统计（可禁用）

禁用方法：
```json
{
  "args": [
    "chrome-devtools-mcp@latest",
    "--no-performance-crux",
    "--no-usage-statistics"
  ]
}
```

### 9.2 远程调试风险

开启远程调试端口后，本地任何应用都可控制浏览器。建议：
- 仅在可信环境使用
- 使用防火墙限制访问
- 定期更换用户数据目录

---

## 10. 参考资源

### 10.1 官方文档

- Chrome DevTools MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp
- MCP 协议规范: https://modelcontextprotocol.io/
- nanobot MCP 文档: （见源码 `nanobot/agent/tools/mcp.py`）

### 10.2 相关文件

- 配置位置: `~/.nanobot/config.json`
- 缓存位置: `~/.cache/chrome-devtools-mcp/`
- 日志位置: `~/.nanobot/logs/gateway.log`

---

## 附录 A: 快速参考卡

### 配置模板
```json
{
  "tools": {
    "mcp_servers": {
      "chrome-devtools": {
        "command": "npx",
        "args": ["-y", "chrome-devtools-mcp@latest", "--headless"],
        "tool_timeout": 60
      }
    }
  }
}
```

### 常用命令
```bash
# 重启 nanobot
pkill -f "nanobot gateway" && nanobot gateway

# 清理缓存
rm -rf ~/.cache/chrome-devtools-mcp/chrome-profile

# 查看日志
tail -f ~/.nanobot/logs/gateway.log
```

### 工具命名规则
```
mcp_{server_name}_{tool_name}

示例:
- mcp_chrome_devtools_navigate_page
- mcp_chrome_devtools_take_screenshot
- mcp_chrome_devtools_click
```

---

**文档结束**  
*配置成功时间: 2026-03-13*  
*维护者: nanobot Agent*
