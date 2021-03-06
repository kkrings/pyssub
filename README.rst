Slurm job submission in Python
==============================

.. image:: https://travis-ci.com/kkrings/pyssub.svg?branch=master
   :target: https://travis-ci.com/kkrings/pyssub
   :alt: Build status

.. image:: https://readthedocs.org/projects/pyssub/badge/?version=latest
   :target: https://pyssub.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation status

.. documentation start

This package provides a thin Python layer on top of the `Slurm`_ workload
manager for submitting Slurm batch scripts into a Slurm queue. Its core
features are:

* Python classes representing a Slurm batch script,
* simple file transfer mechanism between shared file system and node,
* macro support based on Python's format specification mini-language,
* `JSON`_-encoding and decoding of Slurm batch scripts,
* new submission command *ssub*,
* successive submission of Slurm batch scripts, and
* rescue of failed jobs.

This example shows how to submit a JSON-encoded Slurm batch script into a Slurm
queue via *ssub*:

::

   ssub submit --in pyssub_example.json --out pyssub_example.out

The JSON-encoded Slurm batch script *pyssub_example.json* has the following
content:

.. code:: json

   {
      "pyssub_example": {
         "executable": "echo",
         "arguments": "'Hello World!'"
      }
   }

A more detailed introduction is given in the `Getting started`_ guide.

Note
----

I have written this package because I was working with a small Slurm cluster
during my PhD. This cluster was configured in a way that the easiest approach
was to submit multiple single-task Slurm batch scripts instead of a single
multi-task Slurm batch script containing multiple *srun* commands. The package
reflects this approach and therefore does not have to be the best solution for
your cluster.


Installation
------------

This package is a pure Python 3 package (it requires at least Python 3.6) and
does not depend on any third-party package. All releases are uploaded
to `PyPI`_ and the newest release can be installed via

::

   pip install pyssub

I would recommend to create a dedicated virtual Python 3 environment for the
installation (e.g.  via `virtualenvwrapper`_):

::

   source /usr/share/virtualenvwrapper/virtualenvwrapper.sh
   mkvirtualenv -p /usr/bin/python3.6 -i pyssub py3-slurm

If you prefer to work with the newest revision, you can also install the
package directly from `GitHub`_:

::

   pip install 'git+https://github.com/kkrings/pyssub#egg=pyssub'


Contributing
------------

I welcome input from your side, either by creating `issues`_ or via `pull
requests`_. For the latter, please make sure that all unit tests pass. The unit
tests can be executed via

::

   python setup.py test


.. External links
.. _Slurm:
   https://slurm.schedmd.com/

.. _JSON:
   https://www.json.org/

.. _Getting started:
   https://pyssub.readthedocs.io/en/latest/guide.html

.. _PyPI:
   https://pypi.org/project/pyssub/

.. _virtualenvwrapper:
   https://virtualenvwrapper.readthedocs.io/

.. _GitHub:
   https://github.com/kkrings/pyssub

.. _issues:
   https://github.com/kkrings/pyssub/issues

.. _pull requests:
   https://github.com/kkrings/pyssub/pulls
