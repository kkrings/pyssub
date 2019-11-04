#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools


description = "Slurm job submission in Python"

long_description = [description, "\n", "=" * len(description), "\n"]

with open("README.rst") as stream:
    readme = stream.readlines()

select = slice(readme.index(".. documentation start\n") + 1, None)
long_description.extend(readme[select])

setuptools.setup(
    name="pyssub",
    version="0.1",
    author="Kai Krings",
    author_email="kai.krings@posteo.de",
    description=description,
    long_description="".join(long_description),
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
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering"
        ],
    python_requires=">=3.6",
    packages=setuptools.find_packages(exclude=["tests"]),
    package_data={"pyssub": ["py.typed"]},
    scripts=["scripts/ssub"],
    test_suite="tests",
    zip_safe=False)
