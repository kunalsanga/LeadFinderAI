import httpx
from config import settings
from typing import Dict, Optional

async def enrich_with_places(company_name: str) -> Optional[Dict]:
    if not settings.GOOGLE_PLACES_API_KEY or "your_" in settings.GOOGLE_PLACES_API_KEY:
        # Mock mode
        return {
            "name": company_name,
            "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
            "phone": "+1234567890",
            "address": "123 Mock Street",
            "rating": 4.5,
            "reviews": 120,
            "type": "ecommerce_store"
        }

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.nationalPhoneNumber,places.formattedAddress,places.rating,places.userRatingCount,places.primaryType"
    }
    payload = {
        "textQuery": company_name
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            places = data.get("places", [])
            if not places:
                return None
                
            place = places[0] # Take the top result
            
            return {
                "name": place.get("displayName", {}).get("text", company_name),
                "website": place.get("websiteUri", ""),
                "phone": place.get("nationalPhoneNumber", ""),
                "address": place.get("formattedAddress", ""),
                "rating": place.get("rating", 0.0),
                "reviews": place.get("userRatingCount", 0),
                "type": place.get("primaryType", "business")
            }
    except Exception as e:
        print(f"Places API Error for {company_name}: {e}")
        return None
