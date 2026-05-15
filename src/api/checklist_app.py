"""
Checklist 应用 - FastAPI 后端
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from checklist_storage import (
    load_data, add_task, toggle_task, delete_task,
    clear_completed, get_stats
)

# 创建 FastAPI 应用
app = FastAPI(
    title="Checklist 管理器",
    description="一个简单好用的任务清单管理工具",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "..", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "..", "..", "static")

# 确保模板和静态文件目录存在
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# 配置模板引擎
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# 挂载静态文件
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ============== 数据模型 ==============

class AddTaskRequest(BaseModel):
    content: str
    category: str = "默认"


class ToggleTaskRequest(BaseModel):
    task_id: str


class DeleteTaskRequest(BaseModel):
    task_id: str


# ============== API 路由 ==============

@app.get("/")
async def home(request: Request):
    """渲染主页面"""
    return templates.TemplateResponse("checklist.html", {"request": request})


@app.get("/api/tasks")
async def get_tasks():
    """获取所有任务"""
    return {"code": 0, "data": load_data()}


@app.get("/api/stats")
async def get_statsistics():
    """获取统计信息"""
    return {"code": 0, "data": get_stats()}


@app.post("/api/tasks")
async def add_new_task(req: AddTaskRequest):
    """添加新任务"""
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="任务内容不能为空")
    task = add_task(req.content.strip(), req.category.strip() or "默认")
    return {"code": 0, "message": "添加成功", "data": task}


@app.post("/api/tasks/toggle")
async def toggle_new_task(req: ToggleTaskRequest):
    """切换任务完成状态"""
    task = toggle_task(req.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "message": "状态已切换", "data": task}


@app.delete("/api/tasks/{task_id}")
async def remove_task(task_id: str):
    """删除任务"""
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "message": "删除成功"}


@app.post("/api/tasks/clear-completed")
async def clear_done_tasks():
    """清除所有已完成任务"""
    count = clear_completed()
    return {"code": 0, "message": f"已清除 {count} 个已完成任务"}


# ============== 分类管理 ==============

@app.get("/api/categories")
async def get_categories():
    """获取所有分类"""
    tasks = load_data()
    categories = list(set(task.get("category", "默认") for task in tasks))
    return {"code": 0, "data": sorted(categories)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
