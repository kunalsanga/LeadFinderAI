from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
from services.task_manager import task_manager
from services.serp_service import get_urls_from_serp
from services.scraper_service import scrape_text_from_url
from services.llm_service import extract_companies_from_text
from services.places_service import enrich_with_places
from services.meta_service import check_meta_ads
from services.email_scraper import scrape_emails
from services.lead_scorer import calculate_lead_score
import asyncio

router = APIRouter()

class SearchQuery(BaseModel):
    query: str

async def process_search(task_id: str, query: str):
    try:
        task_manager.update_status(task_id, "Searching Google for articles...", 5)
        search_results = await get_urls_from_serp(query)
        
        if not search_results:
            task_manager.update_status(task_id, "Completed", 100, result=[])
            return

        all_companies = set()
        
        # Scrape and extract
        total_urls = len(search_results)
        for index, result in enumerate(search_results):
            progress = 5 + int(40 * (index / total_urls))
            task_manager.update_status(task_id, f"Analyzing page {index+1}/{total_urls}: {result['title'][:30]}...", progress)
            
            text = await scrape_text_from_url(result["link"])
            if text:
                extracted = await extract_companies_from_text(text)
                for comp in extracted:
                    if len(comp) > 2:
                        all_companies.add(comp)
        
        companies_list = list(all_companies)
        total_companies = len(companies_list)
        
        # Save raw companies to the task state so it can be exported
        task = task_manager.get_task(task_id)
        if task:
            task["raw_companies"] = companies_list

        if total_companies == 0:
            task_manager.update_status(task_id, "Completed", 100, result=[])
            return
            
        task_manager.update_status(task_id, f"Extracted {total_companies} unique companies. Enriching data...", 45)
        
        enriched_leads = []
        for index, company_name in enumerate(companies_list):
            progress = 45 + int(55 * (index / total_companies))
            task_manager.update_status(task_id, f"Enriching {company_name} ({index+1}/{total_companies})", progress, current=index+1)
            
            # 1. Google Places Enrichment
            place_data = await enrich_with_places(company_name)
            if not place_data:
                continue # Skip if no place found
                
            lead = {
                "Company Name": place_data.get("name", company_name),
                "Category": place_data.get("type", "Business"),
                "Website": place_data.get("website", ""),
                "Phone": place_data.get("phone", ""),
                "Address": place_data.get("address", ""),
                "Google Rating": place_data.get("rating", 0.0),
                "Reviews": place_data.get("reviews", 0)
            }
            
            # 2. Meta Ads Check
            ads_data = await check_meta_ads(lead["Company Name"])
            lead["Meta Ads (Yes/No)"] = "Yes" if ads_data.get("running_ads") else "No"
            
            # 3. Email Scraping
            if lead["Website"]:
                emails = await scrape_emails(lead["Website"])
                lead["Email"] = ", ".join(emails) if emails else ""
            else:
                lead["Email"] = ""
                
            # 4. Lead Scoring
            lead["Lead Score"] = calculate_lead_score(lead)
            
            enriched_leads.append(lead)
            
        task_manager.update_status(task_id, "Completed", 100, result=enriched_leads)
    except Exception as e:
        import traceback
        traceback.print_exc()
        task_manager.update_status(task_id, f"Error: {str(e)}", 100, error=str(e))

@router.post("/search")
async def start_search(payload: SearchQuery, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id)
    background_tasks.add_task(process_search, task_id, payload.query)
    return {"task_id": task_id}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    status = task_manager.get_task(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status
