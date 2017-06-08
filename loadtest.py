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
editor.importText('yeah');
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
        # wait for worker 4 to edit the pad
        await ev.wait()

        # go to the pad
        await firefox.get(PAD)

        not_loaded = True

        while not_loaded:
            # wait for the pad to fill
            try:
                await firefox.execute_script(_GET)
                el = await firefox.wait_for_element(5, '#padText')
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                asyncio.sleep(1.)
                continue
            else:
                content = await el.get_text()
                not_loaded = content == '(awaiting init)'
                if not_loaded:
                    asyncio.sleep(1.)
        # content is the content of the pad we can check once it's
        # edited by worker 9

    else:
        # worker 4 is adding content into the pad
        # go to the pad
        await firefox.get(PAD)

        not_edited = True
        while not_edited:
            try:
                await firefox.execute_script(_SET)
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                asyncio.sleep(1.)
            else:
                not_edited = False

        ev.set()
