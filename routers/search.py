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
        
        # Define allowed place types
        ALLOWED_TYPES = {
            "clothing_store", "corporate_office", "manufacturer", "store", 
            "beauty_salon", "cosmetics_store", "furniture_store", "home_goods_store", 
            "electronics_store", "food", "shopping", "beauty", "wellness", "consumer goods"
        }
        REJECTED_TYPES = {
            "hospital", "hotel", "gym", "school", "park", "restaurant", 
            "tourist_attraction", "service", "government_office", "bank"
        }
        
        enriched_leads = []
        for index, company_name in enumerate(companies_list):
            progress = 45 + int(55 * (index / total_companies))
            task_manager.update_status(task_id, f"Enriching {company_name} ({index+1}/{total_companies})", progress, current=index+1)
            
            # 1. Google Places Enrichment
            place_data = await enrich_with_places(company_name)
            if not place_data:
                continue # Skip if no place found
                
            # Type filtering
            p_type = place_data.get("type", "").lower()
            if any(rt in p_type for rt in REJECTED_TYPES):
                continue
            if p_type not in ALLOWED_TYPES and p_type != "business" and "headquarters" not in p_type and "corporate" not in p_type:
                continue # Skip rejected types
                
            # Fuzzy matching
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, company_name.lower(), place_data.get("name", "").lower()).ratio()
            if similarity < 0.8:
                continue # Skip if name is too different
                
            lead = {
                "Company Name": place_data.get("name", company_name),
                "Category": place_data.get("type", "Business"),
                "Website": place_data.get("website", ""),
                "Phone": place_data.get("phone", ""),
                "Address": place_data.get("address", ""),
                "Google Rating": place_data.get("rating", 0.0),
                "Reviews": place_data.get("reviews", 0)
            }
            
            # 2. Meta Ads Check (Official API)
            ads_data = await check_meta_ads(lead["Company Name"])
            lead["Meta Ads (Yes/No)"] = "Yes" if ads_data.get("running_ads") else "No"
            
            # 3. Website Scraping and Unified LLM Analysis
            lead["LinkedIn"] = ""
            lead["Instagram"] = ""
            lead["Facebook"] = ""
            lead["Contact Us"] = ""
            lead["Careers Page"] = ""
            lead["Founder"] = ""
            lead["Email"] = ""
            lead["D2C"] = False
            lead["Startup"] = False
            lead["Founded Year"] = 0
            lead["Company Age"] = 0
            lead["Meta Ads Probability"] = 0
            lead["Marketing Technology"] = ""
            
            if lead["Website"]:
                from services.scraper_service import scrape_company_website
                from services.llm_service import analyze_company_profile
                
                web_data = await scrape_company_website(lead["Website"])
                lead["LinkedIn"] = web_data.get("linkedin", "")
                lead["Instagram"] = web_data.get("instagram", "")
                lead["Facebook"] = web_data.get("facebook", "")
                lead["Contact Us"] = web_data.get("contact_us", "")
                lead["Careers Page"] = web_data.get("careers", "")
                lead["Marketing Technology"] = ", ".join(web_data.get("tech_stack", []))
                
                # LLM Profiling
                profile = await analyze_company_profile(lead["Company Name"], web_data.get("text", ""))
                
                # Strict Filters
                if profile.get("company_age", 0) > 5 and profile.get("company_age", 0) != 0:
                    continue
                if not profile.get("startup", False) or profile.get("confidence", 0) < 0.70:
                    continue
                if not profile.get("is_d2c", False):
                    continue
                if profile.get("is_large_enterprise", False):
                    continue
                    
                # Populate fields
                lead["D2C"] = True
                lead["Startup"] = True
                lead["Founded Year"] = profile.get("founded_year", 0)
                lead["Company Age"] = profile.get("company_age", 0)
                lead["Meta Ads Probability"] = profile.get("meta_ads_probability", 50)
                lead["Founder"] = profile.get("founder_name", "")
                
                # Emails
                emails = await scrape_emails(lead["Website"])
                lead["Email"] = ", ".join(emails) if emails else ""
                
            else:
                # No website, skip startup filtering because we don't have enough data
                continue
                
            # 4. Lead Scoring
            lead["Place Type"] = p_type # pass to scorer
            lead["Lead Score"] = calculate_lead_score(lead)
            
            from services.lead_scorer import calculate_target_fit
            lead["Target Fit"] = calculate_target_fit(lead["Lead Score"])
            
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
