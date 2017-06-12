from functools import partial
import os
import binascii
import asyncio
import molotov
from molosonic import setup_browser, teardown_browser
from etherpad import EtherpadLite, Notifier


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
    get_var = molotov.get_var
    firefox = session.browser
    pad = get_var('pad', partial(EtherpadLite, firefox, PAD))
    notifier = get_var('notifier' + str(session.step),
                       factory=Notifier)
    wid = session.worker_id

    if wid != 4:
        # I am NOT worker 4! I read the pad

        # go to the pad
        await pad.visit()

        # wait for worker #4 to edit the pad
        await notifier.wait_for_writer()

        # get the text
        text = get_var('text')

        # read the pad until its text is edited by worker #4
        while True:
            content = await pad.get_text()
            if content == text:
                # notify that the pad was read
                await notifier.one_read()
                break
    else:
        # I amuworker 4! I write in the pad
        if session.step > 1:
            # waiting for the previous readers to have finished
            # before we start a new round
            previous_notifier = get_var('notifier' + str(session.step),
                                        factory=Notifier)
            await previous_notifier.wait_for_readers()

        # generate a random text
        text = binascii.hexlify(os.urandom(128)).decode()
        molotov.set_var('text', text)

        # worker 4 is adding content into the pad
        await pad.visit()
        await pad.set_text(text)

        # sleep 10 seconds before notifying readers
        await asyncio.sleep(10.)
        notifier.written()
