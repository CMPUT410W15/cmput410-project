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
    name='SocialDistribution',
    version = "0.1",
    packages = find_packages(),

    install_requires = get_install_reqs(),

    test_suite = 'nose.collector',
    package_data = {
        'socialdistribution': ['data/*']
    },

    description='An alternative to other social media',
)
