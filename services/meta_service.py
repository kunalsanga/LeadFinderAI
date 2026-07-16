import httpx
from config import settings
from typing import Dict

async def check_meta_ads(company_name: str) -> Dict:
    if not settings.META_ACCESS_TOKEN or "your_" in settings.META_ACCESS_TOKEN:
        # Mock mode
        return {"running_ads": True, "ad_count": 5}
        
    url = "https://graph.facebook.com/v19.0/ads_archive"
    params = {
        "access_token": settings.META_ACCESS_TOKEN,
        "search_terms": company_name,
        "ad_active_status": "ACTIVE",
        "ad_reached_countries": "['IN', 'US']", # Assuming global search
        "search_type": "KEYWORD",
        "fields": "id" # Only need to know if they exist
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            ads = data.get("data", [])
            return {
                "running_ads": len(ads) > 0,
                "ad_count": len(ads)
            }
    except Exception as e:
        print(f"Meta API Error for {company_name}: {e}")
        return {"running_ads": False, "ad_count": 0}
