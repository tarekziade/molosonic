import asyncio
from arsenic.errors import NoSuchElement, ArsenicTimeout, JavascriptError



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


class Notifier(object):
    def __init__(self, readers=5):
        self._current = 1
        self._until = readers
        self._condition = asyncio.Condition()
        self._writer = asyncio.Event()

    def _is_set(self):
        return self._current == self._until

    async def wait_for_writer(self):
        await self._writer.wait()

    async def one_read(self):
        if self._is_set():
            return
        self._current += 1
        if self._current == self._until:
            with await self._condition:
                self._condition.notify_all()

    def written(self):
        self._writer.set()

    async def wait_for_readers(self):
        with await self._condition:
            await self._condition.wait()



class EtherpadLite(object):
    def __init__(self, browser, url, sleep=1.):
        self.browser = browser
        self.url = url
        self.sleep = sleep

    async def visit(self):
        return (await self.browser.get(self.url))

    async def get_text(self):
        while True:
            await asyncio.sleep(self.sleep)
            try:
                await self.browser.execute_script(_GET)
                el = await self.browser.wait_for_element(5, '#padText')
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                continue
            else:
                return (await el.get_text())

    async def set_text(self, text):
        while True:
            await asyncio.sleep(self.sleep)
            try:

                await self.browser.execute_script(_SET % text)
                break
            except (NoSuchElement, ArsenicTimeout, JavascriptError):
                continue
