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

This package is pure Python 3 (it requires at least Python 3.6) and does not
depend on any external package. All releases are uploaded to `PyPI`_ and the
newest release can be installed via :code:`pip install pyssub`.

I would recommend to create a dedicated virtual Python 3 environment for the
installation (e.g.  via `virtualenvwrapper`_):

.. code:: bash

   source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
   mkvirtualenv -p /usr/bin/python3.6 -i pyssub py3-slurm

If you prefer to work with the newest revision, you can also install the
package directly from `GitHub`_:

.. code:: bash

   pip install 'git+https://github.com/kkrings/pyssub#egg=pyssub'


Contributing
------------

I welcome input from your side, either by creating `issues`_ or via `pull
reqests`_. For the latter, please make sure that all unit tests pass. The unit
tests can be executed via :code:`python setup.py test`.


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

.. _GitHub:
   https://github.com/kkrings/pyssub

.. _issues:
   https://github.com/kkrings/pyssub/issues

.. _pull reqests:
   https://github.com/kkrings/pyssub/pulls
