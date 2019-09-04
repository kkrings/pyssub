#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


with open("README.rst") as readme:
    long_description = readme.read()

setuptools.setup(
    name="pyssub",
    version="0.1",
    author="Kai Krings",
    author_email="kai.krings@posteo.de",
    description="Slurm job submission in Python",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/kkrings/pyssub/",
    project_urls={
        "Documentation": "https://pyssub.readthedocs.io/",
        "Source": "https://github.com/kkrings/pyssub/",
        "Tracker": "https://github.com/kkrings/pyssub/issues/"
        },
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering"
        ],
    python_requires=">=3.6",
    packages=setuptools.find_packages(),
    scripts=["scripts/ssub"],
    test_suite="tests")
