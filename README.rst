Molosonic
---------

Molotov + Arsenic + Geckodriver

Installation::

    $ virtualenv .
    $ bin/pip install -r requirements.txt


To run 5 Firefox browsers in parallel, each one doing the test 10 times::

    $ bin/molotov -cxv --max-runs 10 -w 5 loadtest.py

