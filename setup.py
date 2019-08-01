#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


setuptools.setup(
    name="pyssub",
    version="0.1",
    author="Kai Krings",
    author_email="kai.krings@posteo.net",
    description="Simple Python interface to Slurm",
    url="https://github.com/kkrings/pyssub/",
    license="GPLv3",
    packages=setuptools.find_packages(),
    scripts=["bin/ssub"],
    test_suite="test")
