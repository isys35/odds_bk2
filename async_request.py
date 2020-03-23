import asyncio
import aiohttp
import time
import ssl
import certifi

async def fetch_content(url, session, headers):
    async with session.get(url, headers=headers,ssl=ssl.create_default_context(cafile=certifi.where())) as response:
        data = await response.text()
        return data


async def req(urls, headers):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(0,len(urls)):
            task = asyncio.create_task(fetch_content(urls[i], session, headers[i]))
            tasks.append(task)
        data = await asyncio.gather(*tasks)
        return data


def input_reuqests(urls, headers):
    print('...')
    t0 = time.time()
    data = asyncio.run(req(urls, headers))
    t = time.time() - t0
    print(t)
    print('...')
    return data


