#!/usr/bin/env python3
"""钉钉文档集成示例。"""

def main():
    """演示钉钉文档集成。"""
    print("SRM 钉钉文档集成演示")
    
    from skills.srm_dingtalk_docs_bridge.config import DingTalkConfig
    
    config = DingTalkConfig.from_env()
    
    print(f"App Key: {config.app_key[:8] if config.app_key else "N/A"}...")
    print("配置加载成功!")

if __name__ == "__main__":
    main()

