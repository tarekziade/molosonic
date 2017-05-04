import asyncio

from arsenic.engines.aiohttp import Aiohttp
from arsenic.browsers import Firefox
from arsenic.services import Geckodriver


async def example():
    # start geckodriver using aiohttp/asyncio
    async with Geckodriver().run(Aiohttp) as driver:
        # start a new browser session
        async with driver.session(Firefox()) as session:
            # go to example.com
            await session.get('http://example.com')
            # wait up to 5 seconds to get the h1 element from the page
            h1 = await driver.wait(5, session.get_element, 'h1')
            # print the text of the h1 element
            print(await h1.get_text())



loop = asyncio.get_event_loop()
loop.run_until_complete(example())
loop.close()

