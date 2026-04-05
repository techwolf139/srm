# 定时同步 Web 管理界面

## 快速开始

### 1. 安装依赖
```bash
pip install flask celery redis apscheduler watchdog
```

### 2. 启动 Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. 配置环境变量
```bash
export CELERY_REDIS_URL=redis://localhost:6379/0
export SYNC_MODE=automatic
export SYNC_INTERVAL=30
```

### 4. 启动服务
```bash
# 启动 Celery Worker
celery -A app.celery_app worker -l info

# 启动 Celery Beat
celery -A app.celery_app beat -l info

# 启动 Web 服务
python app/web/app.py
```

## Web 界面访问

访问 http://localhost:5000

### API 端点

- `GET /` - 概览页面
- `GET /api/jobs` - 获取任务列表
- `POST /api/jobs/<job_id>/pause` - 暂停任务
- `POST /api/jobs/<job_id>/resume` - 恢复任务
- `POST /api/task/trigger_sync` - 手动触发同步
- `GET /api/task/status/<task_id>` - 获取任务状态

## 监控

Web 界面显示：
- 所有任务的状态（活跃/暂停）
- 下次运行时间
- 暂停/恢复按钮

---

*最后更新时间：2026 年 4 月*