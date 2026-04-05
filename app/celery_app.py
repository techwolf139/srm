"""Celery 应用实例"""
import os
from celery import Celery
from celery.schedules import crontab


# 从环境变量加载配置
REDIS_URL = os.getenv("CELERY_REDIS_URL", "redis://localhost:6379/0")

# 创建 Celery 应用
celery_app = Celery(
    "srm_scheduler",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    beat_scheduler_interval=60,
    
    # 常用任务配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="srm_tasks",
    task_default_routing_key="default",
    
    # 定时任务设置
    # beat_schedule={
    #     "sync-every-5-minutes": {
    #         "task": "app.tasks.sync_docs",
    #         "schedule": 300,  # 5 分钟
    #     },
    # },
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])