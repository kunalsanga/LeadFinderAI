import asyncio
import traceback
from routers.search import process_search
import uuid

async def main():
    task_id = str(uuid.uuid4())
    from services.task_manager import task_manager
    task_manager.create_task(task_id)
    print("Task ID:", task_id)
    await process_search(task_id, 'Bengaluru D2C Brands')
    task = task_manager.get_task(task_id)
    print("Final result:")
    if task:
        for k, v in task.items():
            if k != 'result' and k != 'raw_companies':
                print(k, ":", v)
        print('Total raw companies:', len(task.get('raw_companies', [])) if task.get('raw_companies') else 0)
        print('Total verified leads:', len(task.get('result', [])) if task.get('result') else 0)
    else:
        print("Task not found")

if __name__ == "__main__":
    asyncio.run(main())
