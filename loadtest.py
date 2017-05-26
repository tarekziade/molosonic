from functools import partial
import molotov

from arsenic.engines.aiohttp import Engine, start_process, sleep, Session
from arsenic.browsers import Firefox as _Firefox
from arsenic.services import Geckodriver



@molotov.setup_session()
async def _setup_session(wid, session):
    session.firefox_session = FirefoxSession(session)
    session.firefox = await session.firefox_session.start()


@molotov.teardown_session()
async def _teardown_session(wid, session):
    await session.firefox_session.stop()



class FirefoxSession(object):
    def __init__(self, session):
        self.session = session

    async def start(self):
        async def _init_session(auth=None):
            return Session(self.session, auth)

        Client = Engine(http_session=_init_session,
                        start_process=start_process,
                        sleep=sleep)
        self.gecko = Geckodriver()
        self.driver = await self.gecko.start(Client)
        self.firefox = await self.driver.new_session(_Firefox(), '')
        return self.firefox

    async def stop(self):
        await self.firefox.close()
        await self.driver.close()



@molotov.scenario(1)
async def example(session):
    firefox = session.firefox
    # go to example.com
    await firefox.get('http://example.com')

    # wait up to 5 seconds to get the h1 element from the page
    h1 = await firefox.wait_for_element(5, 'h1')

    # print the text of the h1 element
    print(await h1.get_text())
