import asyncio
import traceback
from config import settings
from services.serp_service import get_urls_from_serp

async def main():
    print("SERP KEY:", repr(settings.SERPAPI_API_KEY))
    print("GEMINI KEY:", repr(settings.GEMINI_API_KEY))
    
    try:
        res = await get_urls_from_serp('Bengaluru D2C Brands')
        print('Result len:', len(res))
    except Exception as e:
        print("CRASH!")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
