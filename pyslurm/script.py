# -*- coding: utf-8 -*-

"""Module containing a class that represents a single-task Slurm batch
script.

"""
import os
from typing import Any, Dict, List


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

    Examples
    --------
    Create a simple Slurm batch script.

    >>> import pyslurm
    >>> script = pyslurm.script.SBatchScript("echo", "'Hello World!'")

    """
    def __init__(self, executable: str, arguments: str = "") -> None:
        """Initialize new instance.

        Parameters
        ----------
        executable : str
            Path to executable
        arguments : str, optional
            Arguments that will be passed to `executable`

        """
        # Executable and arguments
        self.executable: str = executable
        self.arguments: str = arguments

        # Slurm sbatch options
        self.options: Dict[str, Any] = {"ntasks": 1}

        # File transfer mechanism
        self.transfer_executable: bool = False
        self.transfer_input_files: List[str] = []
        self.transfer_output_files: List[str] = []

    def __str__(self) -> str:
        """String representation of Slurm batch script

        The string representation of the Slurm batch script can be used
        to dump the script into a file.

        Returns
        -------
        str
            String representation of Slurm batch script

        """
        return _skeleton.format(**self._config)

    @property
    def _config(self) -> Dict[str, str]:
        """dict(str, str): Keyword arguments for `_skeleton.format`
        """
        config = {
            "executable": "'{}'".format(self.executable),
            "arguments": self.arguments,
            "transfer_executable": str(self.transfer_executable).lower()
            }

        # Make sure that this a single-task job.
        self.options["ntasks"] = 1

        config["slurm_options"] = "\n".join(
            "#SBATCH --{key}={val}".format(key=key, val=val)
            for key, val in self.options.items())

        config["transfer_input_files"] = " ".join(
            "'{}'".format(os.path.abspath(f))
            for f in self.transfer_input_files)

        config["transfer_output_files"] = " ".join(
            "'{}'".format(os.path.abspath(f))
            for f in self.transfer_output_files)

        return config


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


# ---Macro support-------------------------------------------------------------
class SBatchScriptMacro:
    """Macro support for Slurm batch script

    This class allows to insert macros into a Slurm batch script. The
    macro support is based on Python string formats.

    Attributes
    ----------
    script : SBatchScript
        Slurm batch script
    macros : dict(str, object)
        Mapping of macro names to objects representing values

    Examples
    --------
    Create a simple Slurm batch script with a single macro.

    >>> import pyslurm
    >>> script = pyslurm.script.SBatchScript("echo", "{message}")
    >>> macros = {"message": "'Hello World!'"}
    >>> script = pyslurm.script.SBatchScriptMacro(script, macros)

    """
    def __init__(self, script: SBatchScript,
                 macros: Dict[str, Any] = {}) -> None:
        """Initialize new instance.

        Parameters
        ----------
        script : SBatchScript
            Slurm batch script
        macros : dict(str, object), optional
            Mapping of macro names to objects representing values

        """
        self.script: SBatchScript = script
        self.macros: Dict[str, Any] = dict(macros)

    def __str__(self) -> str:
        # Insert macros into keyword arguments that are passed to
        # _skeleton.format.
        config = {
            key: value.format(**self.macros)
            for key, value in self.script._config.items()
            }

        return _skeleton.format(**config)

    # Use the same doc string as for SBatchScript.__str__.
    __str__.__doc__ = SBatchScript.__str__.__doc__
