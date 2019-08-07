pyssub
======

This package provides a thin Python layer on top of the `Slurm`_ workload
manager for submitting Slurm batch scripts into a Slurm queue. It's core
features are:

   * Python classes representing a Slurm batch script,
   * simple file transfer mechanism between shared file system and node,
   * macro support based Python's format specification mini-language,
   * `JSON`_-encoding and decoding of Slurm batch scripts,
   * new submission command `ssub`,
   * successive submission of Slurm batch scripts, and
   * rescue of failed jobs.

Checkout the `pyssub`_ documentation.

.. _Slurm:
   https://slurm.schedmd.com/documentation.html

.. _JSON:
   https://www.json.org/

.. _pyssub:
   https://pyssub.readthedocs.io/en/latest/contents.html
