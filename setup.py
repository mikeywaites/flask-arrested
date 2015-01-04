#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask-Arrested
-----------

A Rest API Framework for Flask.
"""

import os
import sys

from setuptools import setup, find_packages


# Get current directory where setup is running
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

# Change directory
if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

# Paths to requirement files
INSTALL_DEPS = os.path.join('deps', 'install.pip')
TEST_DEPS = os.path.join('deps', 'test.pip')
DEV_DEPS = os.path.join('deps', 'dev.pip')


from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-s']
        self.test_suite = True

    def run_tests(self):
        # import here. outside, the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def read_dependencies(filename):
    """
    Read requirements file and process them into a list
    fpr usage in the setup function

    :param filename: Path to the file to read line by line
    :type filename: string

    :returns: list -- list of requirements
    """

    dependencies = []
    with open(filename) as f:
        for line in f.readlines():
            if not line or line.startswith('#'):
                continue
            dependencies.append(line.strip())
    return dependencies


def read(name):
    """
    Read file in local current working directory and return the contents

    :param name: The name of the file
    :type name: string

    :returns: string -- Contents of file
    """

    return open(name).read()


with open('VERSION') as fh:
    VERSION = fh.read().strip()


setup(
    name='arrested',
    version=VERSION,
    author='Mikey Waites',
    author_email='mikey.waites@gmail.com',
    url='https://github.com/mikeywaites/flask-arrested',
    download_url='https://github.com/mikeywaites/flask-arrested/releases/tag/%s' % VERSION,
    description='A python Rest API framework for flask',
    long_description=read('README.rst'),
    packages=find_packages(
        exclude=["tests"]
    ),
    include_package_data=True,
    zip_safe=False,
    install_requires=read_dependencies(INSTALL_DEPS),
    extras_require={
        'develop': read_dependencies(DEV_DEPS)+read_dependencies(TEST_DEPS)
    },
    tests_require=read_dependencies(TEST_DEPS),
    cmdclass={
        'test': PyTest
    },
    dependency_links=[],
    entry_points={},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
    )
