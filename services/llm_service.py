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

class CompanyProfile(BaseModel):
    founded_year: int = Field(description="Year the company was founded (e.g. 2021). Use 0 if unknown.")
    company_age: int = Field(description="Age of the company in years. Use 0 if unknown.")
    startup: bool = Field(description="True if this is a startup company, False if it is a large enterprise, franchise, or non-startup.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0 for the startup assessment.")
    is_d2c: bool = Field(description="True if this is a Direct-to-Consumer (D2C) brand, False otherwise.")
    d2c_confidence: float = Field(description="Confidence score between 0.0 and 1.0 for the D2C assessment.")
    employee_count: str = Field(description="Estimated employee count range (e.g., '10-50', '500+').")
    is_large_enterprise: bool = Field(description="True if the company is a large enterprise (like Amazon, Flipkart, Infosys, etc.).")
    meta_ads_probability: int = Field(description="Probability (0-100) that this company invests or will invest in Meta Ads.")
    founder_name: str = Field(description="Name of the Founder or CEO. Return empty string if unknown.")

async def analyze_company_profile(company_name: str, website_text: str) -> dict:
    """Uses Gemini to comprehensively profile a company based on its website text."""
    if not settings.GEMINI_API_KEY or "your_" in settings.GEMINI_API_KEY:
        # Mock mode if no valid key
        return {
            "founded_year": 2022, "company_age": 2, "startup": True, "confidence": 0.9,
            "is_d2c": True, "d2c_confidence": 0.9, "employee_count": "10-50",
            "is_large_enterprise": False, "meta_ads_probability": 85, "founder_name": "Mock Founder"
        }
        
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = f"""
You are an expert business analyst assessing '{company_name}'.
Read the website context below and extract the requested fields.
Pay special attention to the founding year, whether they are a D2C brand, and their size.

Website Context:
{website_text[:12000]}
"""
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompanyProfile,
            ),
        )
        
        result_json = response.text
        data = json.loads(result_json)
        return data
        
    except Exception as e:
        print(f"LLM Profile Analysis Error for {company_name}: {e}")
        # Default to safe values that won't skip the lead if API fails
        return {
            "founded_year": 0, "company_age": 0, "startup": True, "confidence": 1.0,
            "is_d2c": True, "d2c_confidence": 1.0, "employee_count": "Unknown",
            "is_large_enterprise": False, "meta_ads_probability": 50, "founder_name": ""
        }
