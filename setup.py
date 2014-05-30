#!/usr/bin/python

from distutils.core import setup
from Cython.Build import cythonize
import os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    packages = ['VisualHashPrivate'],
    py_modules = ['VisualHash'],
    ext_modules = cythonize("VisualHashPrivate/FractalTransform.pyx"),
    license = "BSD",
    name = "visual-hash",
    version = "0.0.0",
    url = "https://github.com/droundy/visual-hash",
    author = "David Roundy",
    author_email = "daveroundy@gmail.com",
    description = ("A package to generate visual hashes."),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
)
