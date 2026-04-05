"""定时任务调度配置"""
from dataclasses import dataclass, field as dataclass_field
from typing import Optional, List, Dict, Any
import os


@dataclass
class SchedulerConfig:
    """定时任务配置"""
    
    # 调度模式 (manual|automatic|hybrid)
    mode: str = "automatic"
    
    # 同步周期（分钟）
    sync_interval_minutes: int = 30
    
    # 支持的 IM 平台
    platforms: Optional[List[str]] = None
    
    # 任务队列配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # 文档过滤配置
    doc_type_filter: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.platforms is None:
            self.platforms = ["feishu", "dingtalk"]
    
    @classmethod
    def from_env(cls) -> "SchedulerConfig":
        """从环境变量加载配置"""
        return cls(
            mode=os.getenv("SYNC_MODE", "automatic"),
            sync_interval_minutes=int(
                os.getenv("SYNC_INTERVAL", "30")
            ),
            platforms=os.getenv(
                "PLATFORMS", "feishu,dingtalk"
            ).split(","),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
        )
    
    @property
    def celery_redis_url(self) -> str:
        """获取 Celery Redis URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "mode": self.mode,
            "sync_interval_minutes": self.sync_interval_minutes,
            "platforms": self.platforms,
            "celery_redis_url": self.celery_redis_url,
        }