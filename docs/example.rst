.. pyssub advanced example
.. _advanced_example:

Advanced example
================

Following up the :ref:`getting-started-guide` guide, this more advanced example
shows how to create the same collection of batch scripts via a Python script.

.. code-block:: sh

   ./example.py \
      --sbatch-name pyssub_example \
      --sbatch-exec /home/ga65xaz/pyssub_example.py \
      --sbatch-jobs 2 \
      --sbatch-stdout /scratch9/kkrings/logs \
      --sbatch-in '/scratch9/kkrings/pyssub_example_input_{macros[jobid]:02d}.txt' \
      --sbatch-out '/scratch9/kkrings/pyssub_example_output_{macros[jobid]:02d}.txt' \
      --in 'pyssub_example_input_{macros[jobid]:02d}.txt' \
      --out 'pyssub_example_output_{macros[jobid]:02d}.txt'

The example script `example.py` looks like this:

.. literalinclude:: example.py
    :linenos:
