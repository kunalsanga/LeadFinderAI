import httpx
from bs4 import BeautifulSoup
import re
import asyncio

async def scrape_text_from_url(url: str, max_chars: int = 15000) -> str:
    """
    Downloads the webpage at the given URL, parses it, and extracts the visible text.
    Limits the text length to max_chars to prevent LLM context explosion.
    """
    try:
        # Some sites block default httpx User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script, style, meta, noscript elements
            for element in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                element.decompose()
                
            # Get text
            text = soup.get_text(separator=' ')
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Truncate
            return text[:max_chars]
            
    except Exception as e:
        print(f"Scraper Error for {url}: {e}")
        return ""

async def scrape_company_website(url: str) -> dict:
    """
    Scrapes the company website for text, social links, and contact us page.
    """
    result = {
        "text": "",
        "linkedin": "",
        "instagram": "",
        "contact_us": ""
    }
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links
            for a in soup.find_all('a', href=True):
                href = a['href']
                href_lower = href.lower()
                if 'linkedin.com/company' in href_lower and not result["linkedin"]:
                    result["linkedin"] = href
                elif 'instagram.com' in href_lower and not result["instagram"]:
                    result["instagram"] = href
                elif ('contact' in href_lower or 'contact-us' in href_lower) and not result["contact_us"]:
                    if href.startswith('/'):
                        result["contact_us"] = url.rstrip('/') + href
                    elif href.startswith('http'):
                        result["contact_us"] = href
                        
            # Get text
            for element in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                element.decompose()
            text = soup.get_text(separator=' ')
            result["text"] = re.sub(r'\s+', ' ', text).strip()[:10000] # Need some text for founder extraction
            
    except Exception as e:
        print(f"Error scraping company website {url}: {e}")
        
    return result
