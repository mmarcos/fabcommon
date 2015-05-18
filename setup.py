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
      version=fabcommon.__version__,
      description='Reusable deployment script in fabric.',
      long_description=fabcommon.__doc__,
      author=fabcommon.__author__,
      author_email='mmarcos@rodesia.org',
      url='https://github.com/mmarcos/fabcommon/',
      py_modules=['fabcommon'],
      scripts=['fabcommon.py'],
      license='MIT',
      platforms = 'any',
     )