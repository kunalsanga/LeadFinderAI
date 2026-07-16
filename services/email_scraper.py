import httpx
from bs4 import BeautifulSoup
import re
from typing import List

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def scrape_emails(url: str, timeout: int = 5) -> List[str]:
    emails = set()
    try:
        # Ensure url has scheme
        if not url.startswith('http'):
            url = 'https://' + url
            
        async with httpx.AsyncClient(verify=False, timeout=timeout) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # Find all text that looks like an email
            text_content = response.text
            found_emails = re.findall(EMAIL_REGEX, text_content)
            
            # Filter out junk extensions
            junk_exts = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', 'sentry.io']
            for email in found_emails:
                email = email.lower()
                if not any(email.endswith(ext) for ext in junk_exts):
                    # Exclude some common non-contact emails
                    if not email.startswith(('sentry', 'noreply', 'no-reply')):
                        emails.add(email)
                        
            return list(emails)
    except Exception as e:
        # Silently fail for timeout or connection errors
        return []
