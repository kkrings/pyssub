.. pyssub documentation master file

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

The package's source code is hosted on `GitHub`_.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   guide
   example

.. toctree::
   :maxdepth: 1
   :caption: Modules:

   sbatch
   scmd
   shist


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. external links

.. _Slurm:
   https://slurm.schedmd.com/documentation.html

.. _JSON:
   https://www.json.org/

.. _GitHub:
   https://github.com/kkrings/pyssub
