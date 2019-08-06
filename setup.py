#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


setuptools.setup(
    name="pyssub",
    version="0.1",
    author="Kai Krings",
    author_email="kai.krings@posteo.de",
    description="Simple Python interface to Slurm",
    url="https://github.com/kkrings/pyssub/",
    license="GPLv3",
    packages=setuptools.find_packages(),
    scripts=["scripts/ssub"],
    test_suite="tests")
