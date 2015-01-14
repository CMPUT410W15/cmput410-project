#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
from pip.req import parse_requirements


def get_install_reqs():
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    return required


setup(
    name='Cmput410Project',
    version = "0.1",
    packages = find_packages(),

    install_requires = get_install_reqs(),

    package_data = {
        'cmput410-project': ['data/*']
    },

    description='Our Cmput 410 project',
)
