import asyncio
import aiohttp
import time


async def fetch_content(url, session, headers):
    async with session.get(url, headers=headers) as response:
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
    t0 = time.time()
    data = asyncio.run(req(urls, headers))
    t = time.time() - t0
    print(t)
    return data


