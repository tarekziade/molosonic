from functools import partial
import molotov

from arsenic.engines.aiohttp import Engine, start_process, sleep, Session
from arsenic.browsers import Firefox
from arsenic.services import Geckodriver



@molotov.setup_session()
async def _setup_session(wid, session):

    async def _init_session(auth=None):
        return Session(session, auth)

    Client = Engine(http_session=_init_session,
                    start_process=start_process,
                    sleep=sleep)

    session.Client = Client


@molotov.scenario(1)
async def example(session):
    # start geckodriver using aiohttp/asyncio
    async with Geckodriver().run(session.Client) as driver:
        # start a new browser session
        async with driver.session(Firefox()) as firefox:
            # go to example.com
            await firefox.get('http://example.com')
            # wait up to 5 seconds to get the h1 element from the page
            h1 = await driver.wait(5, firefox.get_element, 'h1')
            # print the text of the h1 element
            print(await h1.get_text())
