"""Celery 状态任务"""
from app.tasks.sync_tasks import sync_all_pending_docs, sync_pending_contract_drafts, sync_pending_audit_reports, sync_invoice_match_documents
from celery import shared_task


@shared_task
def trigger_manual_sync(platform: str = "all"):
    """手动触发同步"""
    return sync_all_pending_docs.delay(platform=platform)


@shared_task
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "tasks": {
            "sync_all": sync_all_pending_docs,
            "sync_contracts": sync_pending_contract_drafts,
            "sync_audits": sync_pending_audit_reports,
            "sync_match": sync_invoice_match_documents,
        }
    }