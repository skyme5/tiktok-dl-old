#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from tiktok_dl.version import version

requires = ["requests>=2.23.0", "loguru>=0.2.5", "jsonschema>=3.1.1"]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="tiktok-dl",
    version=version,
    author="Aakash Gajjar",
    author_email="skyme5@gmx.com",
    description="TikTok video downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skyme5/tiktok-dl",
    packages=find_packages(exclude=["tests"]),
    install_requires=requires,
    entry_points={"console_scripts": ["tiktok-dl=tiktok_dl.app:main"],},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="tiktok video downloader",
)
