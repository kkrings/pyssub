Slurm job submission in Python
==============================

This package provides a thin Python layer on top of the `Slurm`_ workload
manager for submitting Slurm batch scripts into a Slurm queue. Its core
features are:

* Python classes representing a Slurm batch script,
* simple file transfer mechanism between shared file system and node,
* macro support based Python's format specification mini-language,
* `JSON`_-encoding and decoding of Slurm batch scripts,
* new submission command `ssub`,
* successive submission of Slurm batch scripts, and
* rescue of failed jobs.

Installation
------------

All releases of :mod:`pyssub` are uploaded to `PyPI`_ and the newest release
can simply be installed via :code:`pip install pyssub`.

Checkout `pyssub`_'s documentation.

.. _Slurm:
   https://slurm.schedmd.com/

.. _JSON:
   https://www.json.org/

.. _pyssub:
   https://pyssub.readthedocs.io/

.. _PyPI:
   https://pypi.org/project/pyssub/
