---
name: im-bot-gateway
description: Use when building enterprise IM bot integrations (飞书, 企业微信, 钉钉), exposing agent capabilities via REST API, or handling bot webhook events
---

# IM Bot Gateway

## Overview

将智能体能力封装为 REST API，接入企业 IM 工具（飞书、企业微信、钉钉），支持群内对话触发智能体执行。

## When to Use

**触发条件：**
- 需要让业务人员在 IM 群内调用智能体
- 需要 Webhook 接收 IM 事件
- 需要消息推送回 IM 群
- 暴露智能体 API 给第三方调用

**不适用：**
- 纯内部 CLI 使用
- 实时性要求极高（建议 WebSocket）

## 架构概览

```
[飞书/企微/钉钉] 
       ↓ Webhook
[FastAPI Gateway] 
       ↓
[智能体 Skill 调度]
       ↓
[结果 → IM 推送]
```

## 支持平台

| 平台 | Webhook | 消息推送 | OAuth |
|------|---------|----------|-------|
| 飞书 | ✅ | ✅ | ✅ |
| 企业微信 | ✅ | ✅ | ✅ |
| 钉钉 | ✅ | ✅ | ✅ |

## FastAPI 服务结构

```python
from fastapi import FastAPI, WebHook, Header
from pydantic import BaseModel

app = FastAPI(title="采购智能体API")

class ProcurementRequest(BaseModel):
    keyword: str
    platforms: list[str] = ["taobao", "jd", "pdd"]
    limit: int = 10

@app.post("/api/procurement/search")
async def procurement_search(request: ProcurementRequest):
    """采购询价接口"""
    result = await product_researcher.search(
        keyword=request.keyword,
        platforms=request.platforms,
        limit=request.limit
    )
    return {"code": 0, "data": result}
```

## 飞书 Bot 集成

### 1. 创建飞书应用

1. 进入[飞书开放平台](https://open.feishu.cn)
2. 创建企业自建应用
3. 配置机器人能力
4. 获取 App ID 和 App Secret

### 2. Webhook 事件接收

```python
from fastapi import Header, Request
import secrets

@app.post("/webhook/feishu")
async def feishu_webhook(
    request: Request,
    x_lark_signature: str = Header(None)
):
    """飞书 Webhook 事件接收"""
    body = await request.json()
    
    # 验证签名
    if not verify_feishu_signature(body, x_lark_signature):
        return {"error": "invalid signature"}
    
    # 处理事件
    event = body.get("event", {})
    if event.get("type") == "im.message.receive_v1":
        message = event["message"]["content"]
        return await handle_feishu_message(message)
    
    return {"code": 0}
```

### 3. 消息发送

```python
from feishu import FeishuClient

def send_feishu_message(receive_id: str, msg_type: str, content: dict):
    """发送飞书消息"""
    client = FeishuClient(app_id, app_secret)
    client.message.create(
        receive_id_type="open_id",
        receive_id=receive_id,
        msg_type=msg_type,
        content=json.dumps(content)
    )
```

## 企业微信 Bot 集成

### 1. 创建企业微信应用

1. 进入[企业微信管理后台](https://work.weixin.qq.com)
2. 创建应用 → 获取 AgentID 和 Secret
3. 配置企业可信IP

### 2. Webhook 接收

```python
@app.post("/webhook/wecom")
async def wecom_webhook(
    request: Request,
    msg_signature: str = Header(None),
    timestamp: str = Header(None),
    nonce: str = Header(None)
):
    """企业微信 Webhook"""
    body = await request.json()
    
    # 验证签名
    if not verify_wecom_signature(body, msg_signature, timestamp, nonce):
        return {"error": "invalid signature"}
    
    # 处理消息
    msg_type = body.get("msg_type", "")
    content = body.get("content", {}).get("text", "")
    
    if msg_type == "text":
        return await handle_wecom_text(content)
    
    return {"code": 0}
```

### 3. 消息发送

```python
def send_wecom_markdown(content: str, agent_id: str):
    """发送 Markdown 消息"""
    # 使用企业微信应用消息接口
    pass
```

## 钉钉 Bot 集成

```python
@app.post("/webhook/dingtalk")
async def dingtalk_webhook(request: Request):
    """钉钉 Webhook"""
    body = await request.json()
    
    # 钉钉使用加签验证
    # 需配置 Secret
    
    if body.get("msgtype") == "text":
        content = body["text"]["content"]
        return await handle_dingtalk_text(content)
    
    return {"code": 0}
```

## 意图识别路由

```python
INTENT_PATTERNS = {
    r"(询价|比价|查价格).*": "procurement_search",
    r"(供应商|风控|风险).*": "supplier_risk",
    r"(合同|审核).*": "contract_review",
    r"(发票|报销).*": "invoice_match",
    r"(帮助|help).*": "help",
}

def route_intent(message: str) -> str:
    """路由消息到对应技能"""
    for pattern, intent in INTENT_PATTERNS.items():
        if re.search(pattern, message):
            return intent
    return "unknown"
```

## 消息格式化

```python
def format_as_markdown_table(data: list[dict]) -> str:
    """格式化数据为 Markdown 表格"""
    if not data:
        return "未找到数据"
    
    headers = list(data[0].keys())
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    
    for row in data:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    
    return "\n".join(lines)
```

## 部署配置

### Docker Compose

```yaml
version: '3.8'
services:
  im-bot-gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FEISHU_APP_ID=xxx
      - FEISHU_APP_SECRET=xxx
      - WECOM_AGENT_ID=xxx
      - WECOM_AGENT_SECRET=xxx
      - DINGTALK_SECRET=xxx
    restart: unless-stopped
```

### Nginx 反向代理

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 签名验证失败 | 检查 App Secret 是否正确 |
| 消息发送失败 | 检查应用权限配置 |
| 回调地址不通 | 确认公网可达 + HTTPS |
| 消息格式错误 | 飞书/企微/钉钉格式不同 |

## 质量检查表

- [ ] Webhook 签名验证已实现
- [ ] 意图识别路由正常
- [ ] 消息格式化美观
- [ ] 错误处理有降级
- [ ] 日志记录完整
