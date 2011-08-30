Overview
--------

*redgreen* is a daemon for repeatedly running *nosetests* on your code. It is greatly inspired by `tdaemon <http://pypi.python.org/pypi/tdaemon>`_, but aims to be more maintained and simpler to use.

Usage
-----
The simplest case: you want to repeatedly run nosetests on the current directory, with specific arguments passed to nose (everything after the "--" is passed to nose directly)::

  redgreen -- --with-coverage --with-growl

Or you can also monitor other directories (not the current one), with the *-m* flag::

  redgreen -m /dir1 -m /dir2 -- [nose-args]

If you use a tool other than nosetests, you can pass the *-t* flag to specify the utility to execute::

  redgreen -t pytest

