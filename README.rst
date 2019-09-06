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

Checkout `pyssub`_'s documentation.

Installation
------------

All releases of `pyssub` are uploaded to `PyPI`_ and the newest release can be
installed via :code:`pip install pyssub`. Note that `pyssub` is a pure Python 3
package (requires at least Python 3.6), which does not depend on any external
package. It is very likely that you want to install `pyssub` into its own
virtual Python environment (e.g. via `virtualenvwrapper`_):

.. code::

   source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
   mkvirtualenv -p /usr/bin/python3.6 py3-slurm -i pyssub

.. External links
.. _Slurm:
   https://slurm.schedmd.com/

.. _JSON:
   https://www.json.org/

.. _pyssub:
   https://pyssub.readthedocs.io/

.. _PyPI:
   https://pypi.org/project/pyssub/

.. _virtualenvwrapper:
   https://virtualenvwrapper.readthedocs.io/
