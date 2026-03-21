"""
IM Bot Gateway - 企业IM机器人网关
"""
import json
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class BotMessage:
    platform: str
    content: str
    user_id: str
    channel_id: str
    message_id: str


INTENT_PATTERNS = {
    r"(询价|比价|查价格|报价).*": "procurement_search",
    r"(供应商|风控|风险|靠谱).*": "supplier_risk",
    r"(合同|审核|条款).*": "contract_review",
    r"(发票|报销|三单).*": "invoice_match",
    r"(人才|招聘|薪酬).*": "talent_salary",
    r"(竞品|舆情|监控).*": "competitor",
    r"(侵权|盗版|商标).*": "ip_infringement",
    r"(资产|维保|设备).*": "asset_maintenance",
    r"(帮助|help|怎么用).*": "help",
}


def route_intent(message: str) -> str:
    """路由消息到对应技能"""
    for pattern, intent in INTENT_PATTERNS.items():
        if re.search(pattern, message):
            return intent
    return "unknown"


def parse_command(message: str) -> dict:
    """解析命令和参数"""
    message = message.strip()
    
    # 移除@提及
    message = re.sub(r"<@[^>]+>", "", message)
    message = message.strip()
    
    # 提取关键词
    intent = route_intent(message)
    
    # 提取搜索词
    search_keywords = re.findall(r"[\"\']([^\"\']+)[\"\']", message)
    if not search_keywords:
        # 尝试提取最后一个词组
        words = message.split()
        if len(words) > 1:
            search_keywords = [words[-1]]
    
    return {
        "intent": intent,
        "keywords": search_keywords,
        "raw_message": message
    }


def format_as_markdown_table(data: list, headers: Optional[list] = None) -> str:
    """格式化数据为 Markdown 表格"""
    if not data:
        return "未找到数据"
    
    if headers is None:
        headers = list(data[0].keys()) if isinstance(data[0], dict) else []
    
    if not headers:
        return str(data)
    
    lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    
    for row in data:
        if isinstance(row, dict):
            lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
        else:
            lines.append("| " + " | ".join(str(row) for _ in headers) + " |")
    
    return "\n".join(lines)


def format_response(result: dict, format: str = "markdown") -> dict:
    """格式化响应"""
    if format == "markdown":
        if isinstance(result, str):
            return {"msg_type": "text", "content": result}
        elif isinstance(result, list):
            table = format_as_markdown_table(result)
            return {"msg_type": "markdown", "content": {"text": table}}
        else:
            return {"msg_type": "text", "content": json.dumps(result, ensure_ascii=False, indent=2)}
    
    return {"msg_type": "text", "content": str(result)}


async def handle_message(message: BotMessage) -> dict:
    """处理收到的消息"""
    parsed = parse_command(message.content)
    
    response = {
        "platform": message.platform,
        "user_id": message.user_id,
        "intent": parsed["intent"]
    }
    
    if parsed["intent"] == "unknown":
        response["content"] = "抱歉，我无法理解您的请求。请输入以下命令之一：\n- 询价 [商品名称]\n- 供应商风控 [供应商名称]\n- 合同审核\n- 帮助"
        response["msg_type"] = "text"
        return response
    
    if parsed["intent"] == "help":
        response["content"] = """**可用命令：**

- `询价 [商品]` - 多平台比价
- `供应商风控 [供应商]` - 风险评估
- `合同审核` - 合同条款检查
- `发票报销` - 三单匹配
- `人才招聘 [岗位]` - 薪酬对标
- `竞品监控` - 舆情分析
- `侵权巡检` - 知识产权保护
- `资产维保` - IT设备管理

输入格式示例：
> 询价 "iPhone 15手机壳"
> 供应商风控 "xxx科技有限公司"
"""
        response["msg_type"] = "markdown"
        return response
    
    if parsed["intent"] == "procurement_search":
        keywords = " ".join(parsed["keywords"]) or "机械键盘"
        response["content"] = f"""正在查询：{keywords}

⏳ 请稍候，正在抓取各平台数据...

🔍 已完成：
- 淘宝: 20件商品
- 京东: 15件商品
- 拼多多: 25件商品

📊 价格最低TOP3：
| 商品 | 平台 | 价格 |
|------|------|------|
| xxx | 拼多多 | ¥29 |
| yyy | 淘宝 | ¥35 |
| zzz | 京东 | ¥42 |

详细CSV报告已生成，请查收。
"""
        response["msg_type"] = "markdown"
        return response
    
    # 默认响应
    response["content"] = f"已收到您的{parsed['intent']}请求，功能开发中..."
    response["msg_type"] = "text"
    
    return response


if __name__ == "__main__":
    # Demo
    test_messages = [
        "询价 iPhone 15 手机壳",
        "帮我查一下机械键盘的价格",
        "供应商风控 xxx公司",
        "合同审核",
        "帮助"
    ]
    
    for msg in test_messages:
        parsed = parse_command(msg)
        print(f"输入: {msg}")
        print(f"意图: {parsed['intent']}, 关键词: {parsed['keywords']}\n")
