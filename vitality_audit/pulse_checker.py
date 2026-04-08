"""
Feature 4: Pulse Checker

- Asynchronously checks if project/demo links are alive
- Uses HEAD requests for speed
- Returns structured result (alive/dead/status)
"""

import asyncio
import aiohttp


async def check_url(session, url):
    try:
        async with session.head(url, timeout=5, allow_redirects=True) as response:
            # print({
            #     "url": url,
            #     "status": response.status,
            #     "alive": 200 <= response.status < 400
            # })
            return {
                "url": url,
                "status": response.status,
                "alive": 200 <= response.status < 400
            }
    except Exception as e:
        return {
            "url": url,
            "status": None,
            "alive": False,
            "error": str(e)
        }


async def pulse_check(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


def run_pulse_check(urls):
    return asyncio.run(pulse_check(urls))