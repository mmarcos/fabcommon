#!/usr/bin/env python

import sys
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.version_info < (2,5):
    raise NotImplementedError("You need Python 2.5 or greater to use fabcommon.")

import fabcommon

setup(name='fabric',
      version=fabric.__version__,
      description='Reusable deployment script in fabric.',
      long_description=fabric.__doc__,
      author=bottle.__author__,
      author_email='mmarcos@rodesia.org',
      url='http://bottlepy.org/',
      py_modules=['fabcommon'],
      scripts=['fabcommon.py'],
      license='MIT',
      platforms = 'any',
     )