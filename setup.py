#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages


setup(
    author="Matej Urbas",
    author_email="matej.urbas@gmail.com",
    description="A collection of applications to support the Urbas System.",
    entry_points={
        "console_scripts": [
            "urbackup=urbasys.urbackup.app:main",
        ]
    },
    include_package_data=True,
    keywords="urbasys",
    name="urbasys",
    packages=find_packages(include=["urbasys"]),
    test_suite="tests",
)
