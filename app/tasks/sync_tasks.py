"""文档同步任务实现"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_all_pending_docs(self, platform: Optional[str] = None) -> Dict[str, Any]:
    """同步所有待同步的文档"""
    logger.info(f"开始同步待同步文档，平台：{platform or 'all'}")
    
    start_time = datetime.now()
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "logs": [],
    }
    
    try:
        # 获取待同步文档
        pending_docs = _get_pending_documents(platform)
        
        if not pending_docs:
            logger.info("没有待同步的文档")
            results["skipped"] = len(pending_docs)
            return results
        
        logger.info(f"同步 {len(pending_docs)} 个文档")
        
        # 逐文档同步
        for doc_meta in pending_docs:
            result = _sync_single_doc(doc_meta, platform)
            results["logs"].append(result)
            
            if result.get("status") == "success":
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"同步完成：成功{results['success']}，失败{results['failed']}")
        
    except Exception as e:
        logger.error(f"同步失败：{e}")
        results["failed"] = 1
        raise self.retry(exc=str(e), countdown=300)
    
    return results


@shared_task(bind=True, max_retries=3)
def sync_pending_contract_drafts(self, doc_type_filter: Optional[List[str]] = None) -> Dict[str, Any]:
    """同步待同步的合同草稿"""
    logger.info("开始同步合同草稿")
    
    pending_docs = _get_pending_documents()
    
    results = {
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "doc_ids": [],
    }
    
    for doc_meta in pending_docs:
        if doc_meta.doc_type == "contract_draft":
            try:
                _sync_contract_draft(doc_meta)
                results["success"] += 1
                results["doc_ids"].append(doc_meta.doc_id)
            except Exception as e:
                logger.error(f"同步合同草稿失败 {doc_meta.doc_id}: {e}")
                results["failed"] += 1
    
    return results


@shared_task
def sync_pending_audit_reports() -> Dict[str, Any]:
    """同步待同步的审核报告"""
    logger.info("开始同步审核报告")
    
    pending_docs = _get_pending_documents()
    
    results = {
        "success": 0,
        "failed": 0,
        "doc_ids": [],
    }
    
    for doc_meta in pending_docs:
        if doc_meta.doc_type == "audit_report":
            try:
                _sync_audit_report(doc_meta)
                results["success"] += 1
                results["doc_ids"].append(doc_meta.doc_id)
            except Exception as e:
                logger.error(f"同步审核报告失败 {doc_meta.doc_id}: {e}")
                results["failed"] += 1
    
    return results


@shared_task
def sync_invoice_match_documents() -> Dict[str, Any]:
    """同步待同步的三单匹配文档"""
    logger.info("开始同步三单匹配文档")
    
    pending_docs = _get_pending_documents()
    
    results = {
        "success": 0,
        "failed": 0,
        "doc_ids": [],
    }
    
    for doc_meta in pending_docs:
        if "invoice_match" in doc_meta.doc_type:
            try:
                _sync_invoice_match(doc_meta)
                results["success"] += 1
                results["doc_ids"].append(doc_meta.doc_id)
            except Exception as e:
                logger.error(f"同步匹配文档失败 {doc_meta.doc_id}: {e}")
                results["failed"] += 1
    
    return results


def _get_pending_documents():
    """获取待同步文档列表"""
    from app.storage.storage import StorageManager
    
    storage = StorageManager()
    return storage.get_pending_documents()


def _sync_single_doc(doc_meta, platform: Optional[str] = None):
    """同步单个文档"""
    return {
        "doc_id": doc_meta.doc_id,
        "status": "pending",
        "platform": platform,
    }


def _sync_contract_draft(doc_meta):
    """同步合同草稿"""
    pass


def _sync_audit_report(doc_meta):
    """同步审核报告"""
    pass


def _sync_invoice_match(doc_meta):
    """同步三单匹配文档"""
    pass