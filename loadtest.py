from functools import partial
import os
import binascii
import asyncio
from arsenic.errors import NoSuchElement, ArsenicTimeout, JavascriptError

from molosonic import setup_browser, teardown_browser
import molotov
from etherpad import EtherpadLite


PAD = 'http://pad.mocotoolsprod.net/p/molosonic'


class Counter(object):
    def __init__(self, until):
        self._current = 1
        self._until = until
        self._condition = asyncio.Condition()

    def _is_set(self):
        return self._current == self._until

    async def incr(self):
        if self._is_set():
            return
        self._current += 1
        if self._current == self._until:
            with await self._condition:
                self._condition.notify_all()

    async def wait(self):
        with await self._condition:
            await self._condition.wait()


@molotov.global_setup()
def init_test(args):
    if args.workers < 5:
        raise Exception('We need at least 5 workers for that test')


@molotov.setup_session()
async def _setup_session(wid, session):
    await setup_browser(session)


@molotov.teardown_session()
async def _teardown_session(wid, session):
    await teardown_browser(session)



@molotov.scenario(1)
async def example(session):
    firefox = session.browser
    pad = molotov.get_var('pad', partial(EtherpadLite, firefox, PAD))
    write = molotov.get_var('write' + str(session.step), factory=asyncio.Event)
    reads = molotov.get_var('reads' + str(session.step),
                            factory=partial(Counter, 5))
    wid = session.worker_id

    if wid != 4:
        # go to the pad
        await pad.visit()

        # wait for worker 4 to edit the pad
        await write.wait()
        text = molotov.get_var('text')

        while True:
            await asyncio.sleep(1.)

            # wait for the pad to fill
            try:
                content = await pad.get_text()
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                continue

            if content == text:
                await reads.incr()
                break
    else:
        if session.step > 1:
            # waiting for the previous readers to have finished
            # before we start a new round
            await molotov.get_var('reads' + str(session.step - 1)).wait()

        text = binascii.hexlify(os.urandom(128)).decode()
        molotov.set_var('text', text)

        # worker 4 is adding content into the pad
        await pad.visit()
        await pad.set_text(text)
        await asyncio.sleep(10.)
        write.set()
