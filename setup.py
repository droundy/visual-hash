#!/usr/bin/python

from setuptools import setup, find_packages, Extension
try:
    from Cython.Build import cythonize
except:
    def cythonize(x):
        return [Extension(x[:-4], [x[:-4]+'.c'])]
import os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    packages = find_packages(),
    install_requires = [
        "Cython", 'pycrypto'
        ],
    setup_requires = [
        "Cython",
        ],
    py_modules = ['VisualHash'],
    ext_modules = cythonize("VisualHashPrivate/FractalTransform.pyx"),
    license = "BSD",
    name = "visual-hash",
    version = "0.0.0.9",
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
