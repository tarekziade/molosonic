from functools import partial
import os
import binascii
import asyncio

import molotov
from molosonic import setup_browser, teardown_browser

from etherpad import EtherpadLite, Counter


PAD = 'http://pad.mocotoolsprod.net/p/molosonic'


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
        # I am NOT worker 4! I read the pad

        # go to the pad
        await pad.visit()

        # wait for worker #4 to edit the pad
        await write.wait()

        # get the text
        text = molotov.get_var('text')

        # read the pad until its text is edited by worker #4
        while True:
            content = await pad.get_text()
            if content == text:
                # notify that the pad was read
                await reads.incr()
                break
    else:
        # I am worker 4! I write in the pad
        if session.step > 1:
            # waiting for the previous readers to have finished
            # before we start a new round
            await molotov.get_var('reads' + str(session.step - 1)).wait()

        # generate a random text
        text = binascii.hexlify(os.urandom(128)).decode()
        molotov.set_var('text', text)

        # worker 4 is adding content into the pad
        await pad.visit()
        await pad.set_text(text)

        # sleep 10 seconds before notifying readers
        await asyncio.sleep(10.)
        write.set()
