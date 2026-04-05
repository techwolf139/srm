"""钉钉文档集成配置"""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DingTalkConfig:
    """钉钉开放平台配置"""
    
    # 企业应用凭证
    app_key: str
    app_secret: str
    
    # 可选配置  
    base_url: str = "https://oapi.dingtalk.com"
    default_folder_token: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "DingTalkConfig":
        """从环境变量加载配置"""
        return cls(
            app_key=os.getenv("DINGTALK_APP_KEY", ""),
            app_secret=os.getenv("DINGTALK_APP_SECRET", ""),
            base_url=os.getenv("DINGTALK_BASE_URL", "https://oapi.dingtalk.com"),
            default_folder_token=os.getenv("DINGTALK_DEFAULT_FOLDER_TOKEN"),
        )