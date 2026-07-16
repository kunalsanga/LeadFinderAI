from typing import Dict, Any

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, task_id: str):
        self.tasks[task_id] = {
            "status": "Starting...",
            "progress": 0,
            "total_items": 0,
            "current_item": 0,
            "result": None,
            "error": None
        }

    def update_status(self, task_id: str, status: str, progress: int, total: int = None, current: int = None, result: list = None, error: str = None):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["progress"] = progress
            if total is not None:
                self.tasks[task_id]["total_items"] = total
            if current is not None:
                self.tasks[task_id]["current_item"] = current
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error is not None:
                self.tasks[task_id]["error"] = error

    def get_task(self, task_id: str):
        return self.tasks.get(task_id)

task_manager = TaskManager()
