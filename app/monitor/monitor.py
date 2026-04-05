"""文档变更监控"""
import logging
from pathlib import Path
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.storage.storage import StorageManager

logger = logging.getLogger(__name__)


class DocumentChangeHandler(FileSystemEventHandler):
    """文档变更处理器"""
    
    def __init__(self, storage: StorageManager, trigger_callback):
        self.storage = storage
        self.trigger_callback = trigger_callback
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        self._handle_document_change(path)
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        self._handle_document_change(path)
    
    def _handle_document_change(self, path: Path):
        """处理文档变更"""
        if path.suffix != ".json":
            return
        
        logger.info(f"检测到文档变更：{path.name}")
        
        # 触发重新同步
        if self.trigger_callback:
            self.trigger_callback()


class DocMonitor:
    """文档监控服务"""
    
    def __init__(self, storage: StorageManager, trigger_callback=None):
        self.storage = storage
        self.trigger_callback = trigger_callback
        self.observer: Optional[Observer] = None
    
    def start(self, monitor_path: str = "./data/doc_chains"):
        """启动监控"""
        event_handler = DocumentChangeHandler(
            self.storage, 
            self.trigger_callback or self._default_callback
        )
        self.observer = Observer()
        self.observer.schedule(event_handler, monitor_path, recursive=False)
        self.observer.start()
        logger.info(f"开始监控文档变更：{monitor_path}")
    
    def stop(self):
        """停止监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            logger.info("停止文档监控")
    
    def _default_callback(self):
        """默认回调函数"""
        logger.info("文档变更，触发同步")


class StorageMonitor:
    """存储监控"""
    
    def __init__(self, storage_path: str = "./data/doc_chains"):
        self.storage_path = Path(storage_path)
    
    def get_all_documents(self) -> List[str]:
        """获取所有文档"""
        docs = []
        for file_path in self.storage_path.glob("*.json"):
            docs.append(file_path.stem)
        return docs
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        return len(self.storage_path.glob("*.json"))