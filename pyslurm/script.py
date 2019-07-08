# -*- coding: utf-8 -*-

"""Module containing a class representing a Slurm batch script

"""


# ---Slurm batch script--------------------------------------------------------
class SBatchScript:
    """Slurm batch script

    Represents a single-task Slurm batch script. Additionally, a simple
    file transfer mechanism between node and shared file systems is
    realized.

    Attributes
    ----------
    executable : str
        Path to executable
    arguments : str
        Arguments that will be passed to `executable`
    options : dict(str, object)
        Mapping of Slurm sbatch options to objects representing values
    transfer_executable : bool
        Transfer `executable` to node
    transfer_input_files : list(str)
        Sequence of input files that are copied to the node before
        executing `executable`
    transfer_output_files : list(str)
        Sequence of output files that are moved after
        executing `executable`

    """
    def __init__(self, executable, arguments=""):
        # Executable and arguments
        self.executable: str = executable
        self.arguments: str = arguments

        # Slurm sbatch options
        self.options = {"ntasks": 1}

        # File transfer mechanism
        self.transfer_executable = False
        self.transfer_input_files = []
        self.transfer_output_files = []

    def __str__(self):
        """String representation of Slurm batch script

        The string representation of the Slurm batch script can be used
        to dump the script into a file.

        Returns
        -------
        str
            String representation of Slurm batch script

        """
        # Make sure that this a single-task job.
        self.options["ntasks"] = 1

        slurm_options = "\n".join(
            "#SBATCH --{key}={value}".format(key=k, value=v)
            for k, v in self.options.items())

        transfer_input_files = " ".join(
            "'{}'".format(f) for f in self.transfer_input_files)

        transfer_output_files = " ".join(
            "'{}'".format(f) for f in self.transfer_output_files)

        script = _skeleton.format(
            slurm_options=slurm_options,
            executable=self.executable,
            arguments=self.arguments,
            transfer_executable=str(self.transfer_executable).lower(),
            transfer_input_files=transfer_input_files,
            transfer_output_files=transfer_output_files)

        return script


# ---Batch script skeleton-----------------------------------------------------
_skeleton = """#!/usr/bin/env bash

{slurm_options}

echo "Working on node `hostname`."

echo 'Create working directory:'
workdir="slurm_job_$SLURM_JOB_NAME"
mkdir -v $workdir
cd $workdir

executable={executable}
transfer_executable={transfer_executable}

if [ "$transfer_executable" = "true" ]
then
    echo 'Transfer executable to node:'
    cp -v $executable .
    executable=./`basename $executable`
fi

inputfiles=({transfer_input_files})

echo 'Transfer input files to node:'
for inputfile in ${{inputfiles[*]}}
do
    cp -v $inputfile .
done

echo 'Execute...'
$executable {arguments}

outputfiles=({transfer_output_files})

echo 'Transfer output files:'
for outputfile in ${{outputfiles[*]}}
do
    mv -v `basename $outputfile` $outputfile
done

echo 'Remove working directory:'
cd ..
rm -rv $workdir
"""
