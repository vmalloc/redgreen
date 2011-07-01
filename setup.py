
import os
import itertools
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "redgreen", "__version__.py")) as version_file:
    exec version_file.read()

_INSTALL_REQUIRES = []
try:
    import argparse
except ImportError:
    _INSTALL_REQUIRES.append("argparse")

setup(name="redgreen",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2.6",
          ],
      description="(Yet another) nosetests daemon",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      install_requires=_INSTALL_REQUIRES,
      entry_points = dict(
          console_scripts=["redgreen = redgreen.scripts:main"],
      )
      )
