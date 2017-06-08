import os
import binascii
import asyncio
from arsenic.errors import NoSuchElement, ArsenicTimeout, JavascriptError

from molosonic import setup_browser, teardown_browser
import molotov


PAD = 'http://pad.mocotoolsprod.net/p/molosonic'


@molotov.global_setup()
def test_starts(args):
    molotov.set_var('event', asyncio.Event())


@molotov.setup_session()
async def _setup_session(wid, session):
    await setup_browser(session)


@molotov.teardown_session()
async def _teardown_session(wid, session):
    await teardown_browser(session)


_SET = """
var editor = require('ep_etherpad-lite/static/js/pad_editor').padeditor.ace;
editor.importText('%s');
"""


_GET = """
var text = require('ep_etherpad-lite/static/js/pad_editor').padeditor.ace.exportText();

var div = document.getElementById('padText');
if (!div) {
    var div = document.createElement('div');
    div.id = 'padText';
    document.body.appendChild(div);
}

div.textContent = text;

"""



@molotov.scenario(1)
async def example(session):
    firefox = session.browser
    ev = molotov.get_var('event')
    wid = session.worker_id

    if wid != 4:
        # go to the pad
        await firefox.get(PAD)

        # wait for worker 4 to edit the pad
        await ev.wait()
        text = molotov.get_var('text')

        while True:
            await asyncio.sleep(1.)

            # wait for the pad to fill
            try:
                await firefox.execute_script(_GET)
                el = await firefox.wait_for_element(5, '#padText')
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                continue

            content = await el.get_text()
            if content == text:
                break
    else:

        text = binascii.hexlify(os.urandom(128)).decode()
        molotov.set_var('text', text)

        # worker 4 is adding content into the pad
        # go to the pad
        await firefox.get(PAD)
        while True:
            await asyncio.sleep(1.)
            try:
                await firefox.execute_script(_SET % text)
                break
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                continue

        #import pdb; pdb.set_trace()  <---- WHY IS THIS NEEDED
        ev.set()
