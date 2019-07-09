# -*- coding: utf-8 -*-

"""Module containing a class representing a Slurm batch script

"""
import collections.abc
import configparser


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
        self.executable = executable
        self.arguments = arguments

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

    @classmethod
    def load(cls, config):
        """Load Slurm batch script from disk.

        Load Slurm batch script from disk based on Python's simple
        configuration language:

        .. code-block:: ini

            [options]
            ntasks = 1

            [executable]
            command = echo
            arguments = 'Hello World!'
            transfer_executable = false

        Input and output files for the transfer mechanism can be listed
        in ``transfer_input_files`` and ``transfer_output_files``,
        respectively.

        Parameters
        ----------
        config : ConfigParser
            Description of Slurm batch script

        Returns
        -------
        SBatchScript
            Slurm batch script

        """
        script = cls(
            executable=config["executable"]["command"],
            arguments=config["executable"]["arguments"])

        script.options.update(config["options"])

        script.transfer_executable = config.getboolean(
            "executable", "transfer_executable")

        if "transfer_input_files" in config:
            script.transfer_input_files.extend(
                config["transfer_input_files"])

        if "transfer_output_files" in config:
            script.transfer_output_files.extend(
                config["transfer_output_files"])

        return script

    def save(self, filename):
        """Save Slurm batch script to disk.

        Save Slurm batch script to disk based on Python's simple
        configuration language.

        Parameters
        ----------
        filename : str
            Path to output file

        """
        config = configparser.ConfigParser(allow_no_value=True)

        config["options"] = self.options

        config["executable"] = {
            "command": self.executable,
            "arguments": self.arguments,
            "transfer_executable": self.transfer_executable
            }

        if len(self.transfer_input_files) > 0:
            config["transfer_input_files"] = {
                f: None for f in self.transfer_input_files
                }

        if len(self.transfer_output_files) > 0:
            config["transfer_output_files"] = {
                f: None for f in self.transfer_output_files
                }

        with open(filename, "w") as stream:
            config.write(stream)


# ---Slurm batch script mapping------------------------------------------------
class SBatchScriptDict(collections.abc.MutableMapping):
    """Slurm batch script mapping

    This class can be used to define and save a collection of Slurm jobs
    for later submission. It represents a mapping of job names to Slurm
    batch scripts.

    """
    def __init__(self):
        self._config = configparser.ConfigParser()

    def __getitem__(self, name):
        """Load Slurm batch script.

        Load the saved Slurm batch script of the specified Slurm job.

        Parameters
        ----------
        name : str
            Job name

        Returns
        -------
        SBatchScript
            Slurm batch script

        """
        macros = dict(self._config[name])

        config = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation(),
            allow_no_value=True)

        config.read(macros.pop("script"))
        config["macros"] = macros

        return SBatchScript.load(config)

    def add_job(self, name, script, **macros):
        """Insert Slurm job into mapping.

        Parameters
        ----------
        name : str
            Job name
        script : str
            Path to saved Slurm batch script
        macros
            Optional macros

        """
        config = {"script": script}
        config.update(macros)
        self._config[name] = config

    def __setitem__(self, name, config):
        """Insert Slurm job into mapping.

        Parameters
        ----------
        name : str
            Job name
        config : dict
            Mapping containing the path ``script`` to the saved Slurm
            batch script; remaining entries are treated as macros.

        """
        macros = dict(config)
        script = macros.pop("script")
        self.add(name, script, **macros)

    def __delitem__(self, name):
        """Remove Slurm job from mapping.

        Parameters
        ----------
        name : str
            Job name

        """
        self._config.pop(name)

    def __len__(self):
        """Number of Slurm jobs"""
        return len(self._config.sections())

    def __iter__(self):
        """Iterate over job names."""
        return iter(self._config.sections())

    def save(self, filename):
        """Save batch script mapping.

        Save batch script mapping to disk based on Python's simple
        configuration language.

        Parameters
        ----------
        filename : str
            Path to output file

        """
        with open(filename, "w") as stream:
            self._config.write(stream)


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
rm -rv $workdir"""
