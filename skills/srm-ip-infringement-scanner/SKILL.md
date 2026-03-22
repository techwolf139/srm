---
name: ip-infringement-scanner
description: Use when monitoring trademark infringement on Chinese e-commerce platforms, identifying counterfeit sellers, or generating evidence reports for IP protection
---

# IP Infringement Scanner

## Overview

定期在电商平台（淘宝、京东、拼多多）搜索公司商标或产品外观，识别低价盗版或未授权店铺，自动记录链接留存证据，用于知识产权保护。

## When to Use

**触发条件：**
- 品牌新品发布后
- 定期巡检（每周/每月）
- 发现假货投诉需求
- 电商大促前（618/双11）
- 竞品举报配合

**不适用：**
- 实时打假（建议专业打假公司）
- 全平台覆盖（建议专业维权服务）

## 支持平台

| 平台 | 搜索难度 | 投诉入口 |
|------|----------|----------|
| 淘宝/天猫 | 中 | 阿里知识产权保护平台 |
| 京东 | 低 | 京东维权平台 |
| 拼多多 | 高 | 拼多多知产保护 |
| 1688 | 中 | 1688举报中心 |

## 监控类型

| 类型 | 说明 | 证据要求 |
|------|------|----------|
| 商标侵权 | 未经授权使用注册商标 | 商标证 + 侵权截图 |
| 专利侵权 | 外观/实用新型/发明专利 | 专利证书 + 侵权证据 |
| 著作权侵权 | 图片、文案抄袭 | 著作权登记证 + 侵权内容 |
| 假货 | 假冒品牌 | 鉴定报告 + 购买鉴定 |

## 数据结构

```python
class InfringementCase:
    platform: str           # 平台
    shop_name: str         # 店铺名称
    shop_url: str          # 店铺链接
    product_url: str       # 商品链接
    product_name: str      # 商品名称
    price: float           # 售价
    infringement_type: str # 侵权类型
    evidence_screenshots: list[str]  # 证据截图URL
    first_seen: str        # 首次发现时间
    last_checked: str      # 最后检查时间
    status: str            # pending/reported/resolved
```

## 证据留存

```python
def capture_evidence(
    url: str,
    product_name: str,
    infringement_type: str
) -> dict:
    """
    使用Playwright截图留存证据
    """
    import base64
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        # 截图商品页
        screenshot = page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode()
        
        # 提取关键信息
        info = {
            "shop_name": page.locator(".shop-name").text_content(),
            "product_title": page.locator(".product-title").text_content(),
            "price": page.locator(".price").text_content(),
        }
        
        browser.close()
    
    return {
        "screenshot": screenshot_b64,
        "info": info,
        "captured_at": datetime.now().isoformat()
    }
```

## 投诉流程

### 淘宝/天猫投诉

```python
def report_taobao(case: InfringementCase) -> dict:
    """在阿里知产平台提交投诉"""
    # 需注册阿里知产账号并完成资质认证
    # API: https://ipp.alibaba.com
    pass
```

### 京东投诉

```python
def report_jd(case: InfringementCase) -> dict:
    """在京东维权平台提交投诉"""
    # 京东维权入口
    pass
```

## 证据报告生成

```markdown
# 知识产权侵权证据报告

**生成时间:** 2026-03-21
**涉及品牌:** [品牌名称]
**侵权类型:** 商标侵权

---

## 侵权概况

| 平台 | 侵权店铺数 | 商品数 | 均价 |
|------|-----------|--------|------|
| 淘宝 | 12 | 45 | ¥89 |
| 天猫 | 2 | 5 | ¥156 |
| 京东 | 5 | 12 | ¥95 |
| 拼多多 | 28 | 120 | ¥45 |

---

## 重点侵权店铺

### 1. xxx旗舰店（淘宝）

**店铺链接:** https://shopxxx.taobao.com
**侵权商品数:** 15
**平均价格:** ¥89 (正品价: ¥299)

**典型侵权商品:**
- [商品链接] - ¥89 (我司正品: ¥299)
- [商品链接] - ¥95 (我司正品: ¥299)

**证据截图:** (附件)

---

## 维权建议

1. **优先处理:** 销量大、评分高的店铺
2. **投诉渠道:** 
   - 淘宝: 阿里知产保护平台
   - 京东: 京东维权平台
3. **处理周期:** 3-7个工作日
4. **后续行动:** 未下架则发律师函
```

## 侵权判断标准

| 侵权类型 | 判断标准 |
|----------|----------|
| 商标相似 | 商标文字/图形相似度>80% |
| 价格异常 | 售价<正品价的30% |
| 销量异常 | 短时间内销量激增 |
| 图文抄袭 | 商品图片相似度>70% |

## 常见错误

| 错误 | 纠正 |
|------|------|
| 证据不完整 | 需包含店铺名+商品+价格+时间 |
| 未保存原图 | 截图+源文件双重保存 |
| 投诉材料不全 | 商标证/专利证必须有效期内 |
| 错过投诉时限 | 淘宝45天、京东30天 |

## 质量检查表

- [ ] 每个侵权证据有完整截图
- [ ] 侵权店铺信息完整（名称、链接）
- [ ] 侵权类型判断有依据
- [ ] 报告包含投诉建议
- [ ] 证据文件按时间归档
