#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

REQUIREMENTS = ["click==7.0", "requests==2.19.1"]

SETUP_REQUIREMENTS = ["pytest-runner"]

TEST_REQUIREMENTS = ["pytest"]

setup(
    author="Matej Urbas",
    author_email="matej.urbas@gmail.com",
    description="A collection of applications to support the Urbas System.",
    entry_points={
        "console_scripts": [
            "urbasys=urbasys.app:main",
            "urbackup=urbasys.urbackup.app:main",
        ]
    },
    install_requires=REQUIREMENTS,
    include_package_data=True,
    keywords="urbasys",
    name="urbasys",
    packages=find_packages(include=["urbasys"]),
    setup_requires=SETUP_REQUIREMENTS,
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
)
