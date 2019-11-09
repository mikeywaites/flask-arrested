#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages


# Get current directory where setup is running
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

# Change directory
if SETUP_DIRNAME != "":
    os.chdir(SETUP_DIRNAME)


setup(
    name="arrested_example",
    version="0.0.1",
    description="Example Arrested API",
    long_description="Example Arrested API",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
)
