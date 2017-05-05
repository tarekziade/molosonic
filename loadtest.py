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

    firefox = Firefox(Client)
    _firefox = await firefox.start()
    session.firefox = _firefox
    session._firefox = firefox


@molotov.teardown_session()
async def _teardown_session(wid, session):
    await session._firefox.stop()



class Firefox(object):
    def __init__(self, client):
        self.client = client

    async def start(self):
        self.driver_cm = Geckodriver()
        self.driver = await self.driver_cm.start(self.client)
        firefox = await self.driver.new_session(_Firefox(), '')
        firefox.wait = self.driver.wait
        self.firefox = firefox
        return firefox

    async def stop(self):
        await self.firefox.close()
        await self.driver.close()


@molotov.scenario(1)
async def example(session):
    firefox = session.firefox
    # go to example.com
    await firefox.get('http://example.com')
    # wait up to 5 seconds to get the h1 element from the page
    h1 = await firefox.wait(5, firefox.get_element, 'h1')
    # print the text of the h1 element
    print(await h1.get_text())
