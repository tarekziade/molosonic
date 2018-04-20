from molosonic import setup_browser, teardown_browser
import molotov

@molotov.setup_session()
async def _setup_session(wid, session):
    await setup_browser(session)


@molotov.teardown_session()
async def _teardown_session(wid, session):
    await teardown_browser(session)


@molotov.scenario(1)
async def example(session):
    firefox = session.browser
    # go to example.com
    await firefox.get('http://example.com')

    # wait up to 5 seconds to get the h1 element from the page
    h1 = await firefox.wait_for_element(5, 'h1')

    # print the text of the h1 element
    print(await h1.get_text())
