from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.task_manager import task_manager
from services.excel_export import generate_excel, generate_csv, generate_companies_excel
import os

router = APIRouter()

@router.get("/export/{task_id}")
async def export_results(task_id: str, format: str = "excel"):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task["progress"] != 100 or task["result"] is None:
        raise HTTPException(status_code=400, detail="Task is not complete yet")
        
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    
    if format == "companies":
        companies = task.get("raw_companies")
        if not companies:
            raise HTTPException(status_code=400, detail="No raw companies found to export")
        file_path = os.path.join(export_dir, f"companies_{task_id}.xlsx")
        generate_companies_excel(companies, file_path)
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=f"companies_{task_id}.xlsx")
        
    leads = task["result"]
    if not leads:
        raise HTTPException(status_code=400, detail="No leads found to export")
        
    if format == "excel":
        file_path = os.path.join(export_dir, f"verified_leads_{task_id}.xlsx")
        generate_excel(leads, file_path)
        return FileResponse(file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=f"verified_leads_{task_id}.xlsx")
    elif format == "csv":
        file_path = os.path.join(export_dir, f"verified_leads_{task_id}.csv")
        generate_csv(leads, file_path)
        return FileResponse(file_path, media_type='text/csv', filename=f"verified_leads_{task_id}.csv")
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'excel', 'csv', or 'companies'")
