import sys
import asyncio

from aiohttp import ClientSession
from functools import partial
from arsenic.engines.aiohttp import Session
from arsenic.services import Geckodriver, tasked, check_service_status
from arsenic.utils import free_port
from arsenic.subprocess import get_subprocess_impl
from arsenic import browsers
from arsenic.webdriver import WebDriver
from arsenic.connection import Connection


async def custom_subprocess_based_service(cmd, service_url, log_file,
                                          session=None):
    closers = []
    try:
        impl = get_subprocess_impl()
        process = await impl.start_process(cmd, log_file)
        closers.append(partial(impl.stop_process, process))
        if session is None:
            session = ClientSession()
        closers.append(session.close)
        count = 0
        check = check_service_status
        async with ClientSession() as ping_client:
            while True:
                try:
                    if await tasked(check(ping_client, service_url)):
                        break
                except Exception:
                    # TODO: make this better
                    count += 1
                    if count > 30:

                        raise Exception('not starting?')
                    await asyncio.sleep(0.5)

        return WebDriver(
            Connection(session, service_url),
            closers,
        )
    except Exception:
        for closer in reversed(closers):
            await closer()
        raise


class CustomGeckoDriver(Geckodriver):
    version_check = True
    binary = 'geckodriver'
    log_file = sys.stdout

    def __init__(self, session=None):
        self.session = session

    async def start(self):
        port = free_port()
        await self._check_version()
        return await custom_subprocess_based_service(
            [self.binary, '--port', str(port)],
            f'http://localhost:{port}',
            self.log_file,
            self.session
        )


class FirefoxSession(object):
    def __init__(self, aiohttp_session, bind=''):
        self.aiohttp_session = aiohttp_session
        self.bind = ''

    async def start(self):
        self.service = CustomGeckoDriver(self.aiohttp_session)
        self.browser = browsers.Firefox()
        self.driver = await self.service.start()
        self.arsenic_session = await self.driver.new_session(self.browser,
                                                             bind=self.bind)
        return self.arsenic_session

    async def stop(self):
        await self.arsenic_session.close()
        await self.arsenic_session.driver.close()


async def setup_browser(session):
    session._session = FirefoxSession(session)
    session.browser = await session._session.start()


async def teardown_browser(session):
    await session._session.stop()
