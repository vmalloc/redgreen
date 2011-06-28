Overview
--------

*redgreen* is a daemon for repeatedly running *nosetests* on your code. It is greatly inspired by `tdaemon <http://pypi.python.org/pypi/tdaemon>`_, but aims to be more maintained and simpler to use.

Usage
-----
The simplest case: you want to repeatedly run nosetests on a directory, with specific arguments passed to nose (everything after the "--" is passed to nose directly)::

  redgreen -m <your directory> -- --with-coverage --with-growl
