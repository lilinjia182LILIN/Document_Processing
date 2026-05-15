"""
Checklist 应用 - 数据存储模块
使用 JSON 文件持久化数据
"""
import json
import os
from datetime import datetime
from typing import List, Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "checklist.json")


def load_data() -> List[dict]:
    """加载任务列表"""
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        save_data([])
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_data(data: List[dict]) -> None:
    """保存任务列表"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_task_by_id(task_id: str) -> Optional[dict]:
    """根据 ID 获取任务"""
    tasks = load_data()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def add_task(content: str, category: str = "默认") -> dict:
    """添加新任务"""
    tasks = load_data()
    new_task = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "content": content,
        "category": category,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    tasks.append(new_task)
    save_data(tasks)
    return new_task


def toggle_task(task_id: str) -> Optional[dict]:
    """切换任务完成状态"""
    tasks = load_data()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            save_data(tasks)
            return task
    return None


def delete_task(task_id: str) -> bool:
    """删除任务"""
    tasks = load_data()
    original_len = len(tasks)
    tasks = [task for task in tasks if task["id"] != task_id]
    if len(tasks) < original_len:
        save_data(tasks)
        return True
    return False


def clear_completed() -> int:
    """清除所有已完成任务"""
    tasks = load_data()
    original_len = len(tasks)
    tasks = [task for task in tasks if not task["completed"]]
    deleted_count = original_len - len(tasks)
    save_data(tasks)
    return deleted_count


def get_stats() -> dict:
    """获取统计信息"""
    tasks = load_data()
    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0
    }
