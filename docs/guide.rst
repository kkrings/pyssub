.. pyssub getting started guide
.. _getting-started-guide:

Getting started
===============

Imagine you have an executable that you want to execute on a Slurm batch farm
for a list of input files. Each job should process one input file. Both the
executable and the input file should be copied to the computing node.

#. Create skeleton batch script ``pyssub_example.script``.

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

#. Create batch script collection ``pyssub_example.jobs``.

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

#. Submit batch script collection via `ssub`.

   .. code-block:: sh

      ssub submit \
         --in pyssub_example.jobs \
         --out pyssub_example.out

#. After your jobs are done, collect the failed ones.

   .. code-block:: sh

      ssub rescue \
         --in pyssub_example.out \
         --out pyssub_example.rescue

#. Resubmit failed jobs.

   .. code-block:: sh

      ssub submit \
         --in pyssub_example.jobs \
         --out pyssub_example.out \
         --rescue pyssub_example.rescue
