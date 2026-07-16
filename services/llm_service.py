from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from config import settings
import json

class CompanyExtraction(BaseModel):
    companies: List[str] = Field(description="List of extracted company names")

async def extract_companies_from_text(text: str) -> List[str]:
    """
    Uses Gemini API to extract company names from the given text.
    """
    if not settings.GEMINI_API_KEY or "your_" in settings.GEMINI_API_KEY:
        # Mock if no valid key
        print("GEMINI_API_KEY not valid. Using mock extraction.")
        return []
        
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""
Extract ONLY company names from the following text.
Ignore: headings, cities, states, countries, websites, advertisements, blogs, people, investors, article titles.

Text:
{text}
"""
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompanyExtraction,
            ),
        )
        
        result_json = response.text
        data = json.loads(result_json)
        
        # In case the schema returns a dictionary with 'companies' key
        if isinstance(data, dict) and "companies" in data:
            return data["companies"]
        elif isinstance(data, list):
            return data
            
        return []
        
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return []
