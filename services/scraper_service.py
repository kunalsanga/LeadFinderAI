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

_CACHE = {}

async def scrape_company_website(url: str) -> dict:
    """
    Scrapes the company website for text, social links, contact us page, and marketing tech.
    """
    if url in _CACHE:
        return _CACHE[url]
        
    result = {
        "text": "",
        "linkedin": "",
        "instagram": "",
        "facebook": "",
        "contact_us": "",
        "careers": "",
        "tech_stack": []
    }
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
            
            # Detect Tech Stack from raw HTML
            html_lower = html.lower()
            if 'fbq(' in html_lower or 'fbevents.js' in html_lower: result["tech_stack"].append("Meta Pixel")
            if 'gtag' in html_lower or 'analytics.js' in html_lower: result["tech_stack"].append("Google Analytics")
            if 'googletagmanager.com' in html_lower: result["tech_stack"].append("Google Tag Manager")
            if 'shopify.' in html_lower or 'cdn.shopify.com' in html_lower: result["tech_stack"].append("Shopify")
            if 'woocommerce' in html_lower: result["tech_stack"].append("WooCommerce")
            if 'mage/' in html_lower or 'magento' in html_lower: result["tech_stack"].append("Magento")
            if 'wp-content' in html_lower or 'wordpress' in html_lower: result["tech_stack"].append("WordPress")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            about_url = None
            
            # Extract links
            for a in soup.find_all('a', href=True):
                href = a['href']
                href_lower = href.lower()
                if 'linkedin.com/company' in href_lower and not result["linkedin"]:
                    result["linkedin"] = href
                elif 'instagram.com' in href_lower and not result["instagram"]:
                    result["instagram"] = href
                elif 'facebook.com' in href_lower and not result["facebook"]:
                    result["facebook"] = href
                elif ('contact' in href_lower or 'contact-us' in href_lower) and not result["contact_us"]:
                    if href.startswith('/'): result["contact_us"] = url.rstrip('/') + href
                    elif href.startswith('http'): result["contact_us"] = href
                elif ('career' in href_lower or 'jobs' in href_lower) and not result["careers"]:
                    if href.startswith('/'): result["careers"] = url.rstrip('/') + href
                    elif href.startswith('http'): result["careers"] = href
                elif ('about' in href_lower) and not about_url:
                    if href.startswith('/'): about_url = url.rstrip('/') + href
                    elif href.startswith('http') and url in href: about_url = href
                        
            # Get homepage text
            for element in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                element.decompose()
            text = soup.get_text(separator=' ')
            text = re.sub(r'\s+', ' ', text).strip()
            
            # If About Us found, fetch it for better founding year extraction
            if about_url:
                try:
                    about_resp = await client.get(about_url, headers=headers)
                    if about_resp.status_code == 200:
                        about_soup = BeautifulSoup(about_resp.text, 'html.parser')
                        for element in about_soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                            element.decompose()
                        about_text = about_soup.get_text(separator=' ')
                        about_text = re.sub(r'\s+', ' ', about_text).strip()
                        text = text + "\n\n--- ABOUT US ---\n\n" + about_text
                except:
                    pass
                    
            result["text"] = text[:15000] # Limit size for LLM context
            
            _CACHE[url] = result
            
    except Exception as e:
        print(f"Error scraping company website {url}: {e}")
        
    return result
