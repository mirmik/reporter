#!/usr/bin/env python3

from wheel.bdist_wheel import bdist_wheel as bdist_wheel_
from setuptools import setup, Extension, Command
from distutils.util import get_platform

import glob
import sys
import os

directory = os.path.dirname(os.path.realpath(__file__))


setup(
    name="reporter",
    packages=["reporter"],
    python_requires='>3.10.0',
    version="0.1.0",
    license="MIT",
    description="Report collector",
    author="mirmik",
    author_email="mirmikns@yandex.ru",
    url="https://github.com/mirmik/reporter",
    long_description=open(os.path.join(
        directory, "README.md"), "r", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    keywords=["testing"],
    classifiers=[],
    package_data={
        "reporter": [
        ]
    },
    include_package_data=True,
    install_requires=[
    ],
    extras_require={},
    entry_points={"console_scripts": [
        "reporter-start=reporter.starter:main_starter",
        "reporter-total=reporter.total:main_reporter",
    ]},
)
