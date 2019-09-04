.. pyssub getting started guide
.. _getting-started-guide:

Getting started
===============

Imagine you have an executable that you want to execute on a Slurm batch farm
for a list of input files. Each job should process one input file. Both the
executable and the input file should be copied to the computing node.

#. Create a skeleton batch script ``pyssub_example_one.json``:

   .. code-block:: json

      {
         "executable": "/home/ga65xaz/pyssub_example.py",
         "arguments": "--in {macros[inputfile]} --out {macros[outputfile]}",
         "options": {
            "job-name": "{macros[jobname]}",
            "ntasks": 1,
            "time": "00:10:00",
            "chdir": "/var/tmp",
            "error": "/scratch9/kkrings/logs/{macros[jobname]}.out",
            "output": "/scratch9/kkrings/logs/{macros[jobname]}.out"
         },
         "transfer_executable": true,
         "transfer_input_files": [
            "/scratch9/kkrings/{macros[inputfile]}"
         ],
         "transfer_output_files": [
            "/scratch9/kkrings/{macros[outputfile]}"
         ]
      }

   The script ``pyssub_example.py`` must be executable. In this example, we use
   macros, which are based on Python's format specification mini-language, for
   the job name and the file names of both the input and the output file.

   .. warning::

      In case of Python scripts, you have to be careful if the shebang starts
      with ``#!/usr/bin/env python`` because Slurm will transfer the user
      environment of the submit node to the computing node. This could lead to
      unwanted results if you for example use `pyssub` from within a dedicated
      virtual Python 3 environment that does not correspond to the one the
      Python script is supposed to use.

#. Create a batch script collection ``pyssub_example.json``:

   .. code-block:: json

      {
         "pyssub_example_00": {
            "script": "/home/ga65xaz/pyssub_example.script",
            "macros": {
               "jobname": "pyssub_example_00",
               "inputfile": "pyssub_example_input_00.txt",
               "outputfile": "pyssub_example_output_00.txt"
            }
         },
         "pyssub_example_01": {
            "script": "/home/ga65xaz/pyssub_example.script",
            "macros": {
               "jobname": "pyssub_example_01",
               "inputfile": "pyssub_example_input_01.txt",
               "outputfile": "pyssub_example_output_01.txt"
            }
         }
      }

   The collection is a mapping of job names to JSON objects that contain
   the **absolute** path to the batch script skeleton and the macro values that
   will be injected into the skeleton.

   .. note::

      By default, the job name is not the one that Slurm will assign to the job
      internally, but it is best practice to tell Slurm to use the same name
      via the Slurm option ``job-name``. In the example above, this is achieved
      with the help of the macro ``jobname``.

#. Submit the batch script collection via `ssub`.
   The `ssub` command also allows you to control the maximum allowed number of
   queuing jobs (the default is 1000) and to specify how long it should wait
   before trying to submit more jobs into the queue (the default is 120
   seconds). The output file `pyssub_example.out` will contain the job name and
   job ID of each submitted job.

   .. code-block:: sh

      ssub submit \
         --in pyssub_example.json \
         --out pyssub_example.out

#. After your jobs are done, collect the failed ones.
   This feature requires the ``sacct`` command to be available, which allows to
   query the Slurm job database. It will query the status of each job listed
   in `pyssub_example.out`` and save the job name and job ID of each finished
   job that has failed.

   .. code-block:: sh

      ssub rescue \
         --in pyssub_example.out \
         --out pyssub_example.rescue

#. If the jobs have failed because of temporary problems with the computing
   node for example, you can simply resubmit only the failed jobs:

   .. code-block:: sh

      ssub submit \
         --in pyssub_example.json \
         --out pyssub_example.out \
         --rescue pyssub_example.rescue

The next step is to use a Python script for creating the same collection of
batch scripts, which is shown in the :ref:`advanced_example` page.
