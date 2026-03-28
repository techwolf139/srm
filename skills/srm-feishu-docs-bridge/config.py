"""飞书文档集成配置"""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class FeishuConfig:
    """飞书API配置"""

    app_id: str
    app_secret: str
    base_url: str = "https://open.feishu.cn/open-apis"

    # 文档相关配置
    default_folder_token: Optional[str] = None  # 默认文件夹
    doc_template_id: Optional[str] = None  # 合同模板文档ID

    @classmethod
    def from_env(cls) -> "FeishuConfig":
        """从环境变量加载配置"""
        return cls(
            app_id=os.getenv("FEISHU_APP_ID", ""),
            app_secret=os.getenv("FEISHU_APP_SECRET", ""),
            base_url=os.getenv("FEISHU_BASE_URL", "https://open.feishu.cn/open-apis"),
            default_folder_token=os.getenv("FEISHU_DEFAULT_FOLDER_TOKEN"),
            doc_template_id=os.getenv("FEISHU_DOC_TEMPLATE_ID"),
        )