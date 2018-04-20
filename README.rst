Molosonic
=========

Molosonic is a Molotov extension to use a real browser in your
`Molotov <http://molotov.readthedocs.io/>`_ tests.

Molosonic integrates `Arsenic <http://arsenic.readthedocs.io>`_ into the Molotov
session, so one browser instance is launched per worker.

Molosonic was not release yet on PyPI, so to try it, make sure you
have Python 3 and virtualenv and geckodriver in the PATH, then::

    $ virtualenv .
    $ bin/python setup.py develop

To make sure your setup works, try this example::

    $ bin/molotov -w 5 --max-runs 1 examples/simple.py

It will run five browsers and interact with example.com

Once installed, you can use **setup_browser** and
**teardown_browser** to create a browser instance.

Load test example:

.. code-block:: python

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


Check out Arsenic documentation for the available API.

To run 5 Firefox browsers in parallel, each one doing the test 10 times::

    $ molotov -cxv --max-runs 10 -w 5 loadtest.py

