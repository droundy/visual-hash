#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension

try:
    from Cython.Build import cythonize
    USE_CYTHON = True
    ext = '.pyx'
except:
    USE_CYTHON = False
    ext = '.c'

extensions = [Extension("VisualHashPrivate.OptimizedFractalTransform",
                        ["VisualHashPrivate/OptimizedFractalTransform"+ext]),
              Extension("VisualHashPrivate.bayes",
                        ["VisualHashPrivate/bayes"+ext])]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

import os
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    packages = ['VisualHash', 'VisualHashPrivate'],
    ext_modules = extensions,
    install_requires = [
        'pycrypto'
        ],
    license = "BSD",
    name = "visual-hash",
    version = "0.0.0.16",
    url = "https://github.com/droundy/visual-hash",
    author = "David Roundy",
    author_email = "daveroundy@gmail.com",
    description = ("A package to generate visual hashes."),
    long_description=read('README'),
    package_data={'': ['*.md']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)
