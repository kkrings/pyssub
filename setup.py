#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


setuptools.setup(
    name="pyslurm",
    version="0.1",
    author="Kai Krings",
    author_email="kai.krings@posteo.net",
    description="Simple Python interface to Slurm",
    url="https://github.com/kkrings/pyslurm/",
    license="GPLv3",
    packages=setuptools.find_packages(),
    scripts=["bin/pyslurm_submit"])
