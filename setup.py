#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages
from junion     import __author__, __version__, __license__

setup(
        name             = 'junion',
        author           = __author__,
        version          = __version__,
        license          = __license__,
        description      = 'junion library',
        author_email     = 'junion@junion.org',
        url              = 'https://github.com/junion-org/junion.git',
        keywords         = 'python',
        packages         = find_packages(),
        install_requires = [],
        )
