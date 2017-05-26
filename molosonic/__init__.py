from functools import partial
from arsenic.engines.aiohttp import Engine, start_process, sleep, Session
from arsenic.browsers import Firefox as _Firefox
from arsenic.services import Geckodriver


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


async def setup_browser(session):
    session._session = FirefoxSession(session)
    session.browser = await session._session.start()


async def teardown_browser(session):
    await session._session.stop()
