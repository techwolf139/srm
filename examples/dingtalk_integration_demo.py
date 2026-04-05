#!/usr/bin/env python3
"""钉钉文档集成示例。"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    """演示钉钉文档集成。"""
    print("SRM 钉钉文档集成演示")
    
    from skills.srm_dingtalk_docs_bridge.config import DingTalkConfig
    
    config = DingTalkConfig.from_env()
    
    app_key = config.app_key[:8] if config.app_key else "N/A"
    print(f"App Key: {app_key}...")
    print("配置加载成功!")

if __name__ == "__main__":
    main()

