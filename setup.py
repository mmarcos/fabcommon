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

setup(name='fabcommon',
      version=fabcommon.__version__,
      description='Reusable deployment script in fabric.',
      long_description=fabcommon.__doc__,
      author=fabcommon.__author__,
      author_email='mmarcos@rodesia.org',
      url='https://github.com/mmarcos/fabcommon/',
      py_modules=['fabcommon'],
      scripts=['fabcommon.py'],
      install_requires=['fabric>=1.10.1'],
      license='MIT',
      platforms = 'any',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],
     )