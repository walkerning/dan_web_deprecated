# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# package meta info
NAME = "dan_web"
VERSION='0.1'
DESCRIPTION = "dan web"
AUTHOR = ""
AUTHOR_EMAIL = ""

# package contents
MODULES = []
PACKAGES = find_packages()
#print PACKAGES


# dependencies
INSTALL_REQUIRES = [] # somany, use requirements.txt
TESTS_REQUIRE = []

here = os.path.abspath(os.path.dirname(__file__))


def read_long_description(filename):
    path = os.path.join(here, 'filename')
    if os.path.exists(path):
        return open(path).read()
    return ''


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_long_description('README.md'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,

    py_modules=MODULES,
    packages=PACKAGES,

    install_requires=INSTALL_REQUIRES, # use requirement.txt
    tests_require=TESTS_REQUIRE,
)
