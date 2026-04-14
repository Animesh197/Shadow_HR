"""
Feature 4: Pulse Checker

- Checks if links are alive
- Uses async for speed
"""

import asyncio
import aiohttp

def clean_url(url):
    """
    Fix common issues in URLs before checking
    """

    if "github.com" in url and url.endswith(".git"):
        url = url.replace(".git", "")

    return url


async def check_url(session, url):
    url = clean_url(url)  

    try:
        async with session.head(
            url,
            timeout=5,
            allow_redirects=True,
            ssl=False
        ) as response:
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