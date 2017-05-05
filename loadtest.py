from functools import partial
import molotov

from arsenic.engines.aiohttp import Engine, start_process, sleep, Session
from arsenic.browsers import Firefox as _Firefox
from arsenic.services import Geckodriver



@molotov.setup_session()
async def _setup_session(wid, session):

    async def _init_session(auth=None):
        return Session(session, auth)

    Client = Engine(http_session=_init_session,
                    start_process=start_process,
                    sleep=sleep)

    session.Client = Client


class Firefox(object):
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        self.driver_cm = Geckodriver().run(self.session.Client)
        driver = await self.driver_cm.__aenter__()
        self.firefox_cm = driver.session(_Firefox())
        firefox = await self.firefox_cm.__aenter__()
        firefox.wait = driver.wait
        return firefox

    async def __aexit__(self, exc_type, exc, tb):
        await self.firefox_cm.__aexit__(exc_type, exc, tb)
        await self.driver_cm.__aexit__(exc_type, exc, tb)



@molotov.scenario(1)
async def example(session):
    async with Firefox(session) as firefox:
            # go to example.com
            await firefox.get('http://example.com')
            # wait up to 5 seconds to get the h1 element from the page
            h1 = await firefox.wait(5, firefox.get_element, 'h1')
            # print the text of the h1 element
            print(await h1.get_text())
