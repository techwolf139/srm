---
name: web-reader
description: Use when fetching web page content via Jina Reader API, extracting clean Markdown from URLs, or reading Chinese web content for LLM processing
---

# Web Reader

## Overview

使用 Jina Reader API 将任意 URL 转换为 LLM 友好的 Markdown 格式。支持任何网页（新闻、论坛、电商、文档等），自动去除广告、导航栏等干扰元素，输出干净的文章内容。

## When to Use

**触发条件：**
- 需要读取某个网页的具体内容
- 抓取的数据用于 LLM 处理或 RAG
- 需要提取中文网页内容（天池、知乎、微信公众号等）
- 替代 Playwright 方案做轻量级网页读取

**不适用：**
- 需要执行 JavaScript 的动态网页（用 Playwright）
- 需要登录后才能访问的页面
- 需要交互操作（点击、滚动）的页面

## Jina Reader API

### 基础用法

```bash
# 方法1：URL 前缀
curl https://r.jina.ai/https://example.com

# 方法2：API endpoint
curl https://r.jina.ai/https://example.com \
  -H "Accept: application/json"
```

### API 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 目标 URL | 必填 |
| `X-Token` | Jina API Key（可选，提高限流） | - |
| `Target-Domain` | 指定域名 | - |

### 返回格式

**Markdown（默认）：**
```markdown
# Article Title

Content paragraphs...
```

**JSON：**
```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "content": "Clean markdown content...",
  "timestamp": "2026-03-21T10:00:00Z"
}
```

## 使用示例

### Python 调用

```python
import requests

def read_url(url: str, api_key: str = None) -> str:
    """使用 Jina Reader 读取网页内容"""
    headers = {}
    if api_key:
        headers["X-Token"] = api_key
    
    response = requests.get(
        f"https://r.jina.ai/{url}",
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch: {response.status_code}")
```

### 读取天池论坛帖子

```python
url = "https://tianchi.aliyun.com/forum/post/1001440"
content = read_url(url)
print(content)
```

### 读取中文内容

```python
# 知乎文章
content = read_url("https://zhuanlan.zhihu.com/p/xxx")

# 微信公众号文章
content = read_url("https://mp.weixin.qq.com/s/xxx")

# 阿里云文档
content = read_url("https://help.aliyun.com/xxx")
```

## 限流说明

| 方案 | RPM | 说明 |
|------|-----|------|
| 无 API Key | 20 RPM | 适合个人使用 |
| 免费 API Key | 500 RPM | 注册获取 |
| 付费 API Key | 5000 RPM | 高频使用 |

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 403/429 | 限流 | 添加 API Key 或等待 |
| 404 | 页面不存在 | 检查 URL |
| 5xx | Jina 服务问题 | 重试 |
| 超时 | 页面加载慢 | 增加 timeout |

## 与 Playwright 对比

| 特性 | Jina Reader | Playwright |
|------|-------------|------------|
| 速度 | 快 | 慢 |
| JavaScript 执行 | 不支持 | 支持 |
| 登录页面 | 不支持 | 支持 |
| 内容质量 | 好（去除噪声） | 原始 HTML |
| 资源消耗 | 低 | 高 |
| 适用场景 | 内容阅读、RAG | 动态网页、交互 |

## 质量检查表

- [ ] URL 正确且可访问
- [ ] 返回内容非空
- [ ] 内容已去除广告和干扰元素
- [ ] Markdown 格式正确
- [ ] 图片 alt 标签已添加描述
