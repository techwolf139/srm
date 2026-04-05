"""定时调度服务"""
import logging
from datetime import datetime
from typing import Optional, List, Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.celery_app import celery_app
from app.scheduler.config import SchedulerConfig

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时调度服务"""
    
    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.scheduler = BackgroundScheduler()
        self._setup_tasks()
    
    def _setup_tasks(self):
        """设置调度任务"""
        # 添加定时同步任务
        interval = self.config.sync_interval_minutes * 60
        
        trigger = IntervalTrigger(
            seconds=interval,
            timezone="Asia/Shanghai"
        )
        
        self.scheduler.add_job(
            func=celery_app.tasks.sync_all_pending_docs,
            trigger=trigger,
            kwargs={"platform": self._get_active_platforms()},
            id="sync_docs_job",
            replace_existing=True,
        )
        
        # 添加健康检查任务
        self.scheduler.add_job(
            func=celery_app.tasks.health_check,
            trigger=IntervalTrigger(hours=1),
            id="health_check_job",
            replace_existing=True,
        )
    
    def start(self):
        """启动调度服务"""
        logger.info("启动调度服务")
        self.scheduler.start()
    
    def stop(self):
        """停止调度服务"""
        logger.info("停止调度服务")
        self.scheduler.shutdown()
    
    def pause_job(self, job_id: str):
        """暂停任务"""
        self.scheduler.pause_job(job_id)
        logger.info(f"暂停任务：{job_id}")
    
    def resume_job(self, job_id: str):
        """恢复任务"""
        self.scheduler.resume_job(job_id)
        logger.info(f"恢复任务：{job_id}")
    
    def get_job_status(self, job_id: str) -> str:
        """获取任务状态"""
        job = self.scheduler.get_job(job_id)
        if job:
            return "active" if job.next_run_time else "paused"
        return "not_found"
    
    def _get_active_platforms(self) -> Optional[str]:
        """获取活跃平台"""
        platforms = self.config.platforms
        if not platforms:
            return None
        return ",".join(platforms)


class SchedulerManager:
    """调度管理器（单例）"""
    
    _instance: Optional["SchedulerManager"] = None
    _service: Optional[SchedulerService] = None
    
    @classmethod
    def get_instance(cls, config: SchedulerConfig = None) -> "SchedulerManager":
        """单例模式"""
        if cls._instance is None:
            if config is None:
                config = SchedulerConfig.from_env()
            
            cls._service = SchedulerService(config)
            cls._instance = cls()
        
        return cls._instance
    
    def start(self):
        """启动服务"""
        if self._service:
            self._service.start()
    
    def stop(self):
        """停止服务"""
        if self._service:
            self._service.stop()
    
    def pause_job(self, job_id: str):
        """暂停任务"""
        if self._service:
            self._service.pause_job(job_id)
    
    def resume_job(self, job_id: str):
        """恢复任务"""
        if self._service:
            self._service.resume_job(job_id)
    
    def get_all_jobs(self) -> List[Dict]:
        """获取所有任务"""
        if self._service:
            jobs = []
            for job in self._service.scheduler.get_all_jobs():
                jobs.append({
                    "id": job.id,
                    "status": self._service.get_job_status(job.id),
                    "next_run": str(job.next_run_time) if job.next_run_time else None,
                })
            return jobs
        return []