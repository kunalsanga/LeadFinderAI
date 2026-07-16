import httpx
from config import settings
from typing import List, Dict

async def get_urls_from_serp(query: str, num_results: int = 30) -> List[Dict[str, str]]:
    if not settings.SERPAPI_API_KEY or "your_" in settings.SERPAPI_API_KEY:
        # Mock mode if no valid key provided
        return [
            {
                "title": f"Mock Article {i}",
                "link": f"https://example.com/article{i}",
                "snippet": "This is a mock article about companies like Mock Company A and Mock Company B."
            } for i in range(1, 4)
        ]
        
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": settings.SERPAPI_API_KEY,
        "num": num_results,
        "engine": "google"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            organic_results = data.get("organic_results", [])
            
            for result in organic_results:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                if link and title:
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
                    
            return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"SerpAPI Error: {e}")
        return []
