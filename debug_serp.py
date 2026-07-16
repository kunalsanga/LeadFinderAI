import asyncio
import httpx
from config import settings
import json
from services.serp_service import get_companies_from_serp

async def main():
    url = "https://serpapi.com/search"
    params = {
        "q": "Bengaluru D2C Brands",
        "api_key": settings.SERPAPI_API_KEY,
        "num": 100,
        "engine": "google"
    }
    
    debug_info = {}
    debug_info['api_key'] = settings.SERPAPI_API_KEY
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            debug_info['status_code'] = response.status_code
            if response.status_code == 200:
                data = response.json()
                debug_info['organic_results_count'] = len(data.get("organic_results", []))
                
                # simulate filtering
                companies = await get_companies_from_serp("Bengaluru D2C Brands")
                debug_info['companies_filtered'] = companies
            else:
                debug_info['error'] = response.text
    except Exception as e:
        debug_info['exception'] = str(e)
        
    with open("debug_serp.json", "w") as f:
        json.dump(debug_info, f, indent=4)

if __name__ == '__main__':
    asyncio.run(main())
