"""SRM 定时同步应用"""
from flask import Flask, jsonify, render_template, request
from functools import wraps

from app.celery_app import celery_app
from app.scheduler.service import SchedulerManager, SchedulerService
from app.scheduler.config import SchedulerConfig

app = Flask(__name__)
app.config["scheduler_config"] = SchedulerConfig.from_env()


@app.route("/")
def index():
    """概览页面"""
    jobs = SchedulerManager.get_instance().get_all_jobs()
    return render_template("index.html", jobs=jobs)


@app.route("/api/jobs")
def get_jobs():
    """获取任务列表"""
    jobs = SchedulerManager.get_instance().get_all_jobs()
    return jsonify({"jobs": jobs})


@app.route("/api/jobs/<job_id>/pause", methods=["POST"])
def pause_job(job_id):
    """暂停任务"""
    SchedulerManager.get_instance().pause_job(job_id)
    return jsonify({"status": "paused", "job_id": job_id})


@app.route("/api/jobs/<job_id>/resume", methods=["POST"])
def resume_job(job_id):
    """恢复任务"""
    SchedulerManager.get_instance().resume_job(job_id)
    return jsonify({"status": "resumed", "job_id": job_id})


@app.route("/api/task/trigger_sync", methods=["POST"])
def trigger_sync():
    """手动触发同步"""
    platform = request.json.get("platform", "all")
    result = celery_app.tasks.sync_all_pending_docs.delay(platform=platform)
    return jsonify({
        "status": "triggered",
        "task_id": result.id,
    })


@app.route("/api/task/status/<task_id>")
def get_task_status(task_id):
    """获取任务状态"""
    result = celery_app.AsyncResult(task_id)
    return jsonify({
        "task_id": task_id,
        "status": result.status,
        "state": str(result.state),
        "result": str(result.result) if result.result else None,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)