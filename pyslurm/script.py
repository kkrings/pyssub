# -*- coding: utf-8 -*-

"""Module containing classes representing a Slurm batch script

"""
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
        Mapping of sbatch options to objects representing values
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
        """Script's string representation"""
        return _skeleton.format(descr=self._description)

    @property
    def _description(self):
        """dict(str, str): Script's description; will be inserted
        into `_skeleton` when script's string representation is called.
        """
        # Make sure that this a single-task job.
        self.options["ntasks"] = 1

        options = "\n".join(
            "#SBATCH --{key}={value}".format(key=k, value=v)
            for k, v in self.options.items())

        transfer_input_files = " ".join(
            "'{}'".format(f) for f in self.transfer_input_files)

        transfer_output_files = " ".join(
            "'{}'".format(f) for f in self.transfer_output_files)

        description = {
            "options": options,
            "executable": self.executable,
            "arguments": self.arguments,
            "transfer_executable": str(self.transfer_executable).lower(),
            "transfer_input_files": transfer_input_files,
            "transfer_output_files": transfer_output_files
            }

        return description


# ---Slurm batch script with macro support-------------------------------------
class SBatchScriptMacro:
    """Slurm batch script with macro support

    The macro support allows to put variables (macros) into the script
    and to reuse it for different values. The macro support is based on
    Python's format specification mini-language.

    Attributes
    ----------
    script : SBatchScript
        Slurm batch script containing macros
    macros : dict(str, object)
        Macro values that are inserted into the script when the script's
        string representation is called.

    Examples
    --------
    Create a script with one macro.

    >>> skeleton = SBatchScript("echo", "'{macros[mg]}'")
    >>> script = SBatchScriptMacro(skeleton, {"msg": "Hello World!"})

    """
    def __init__(self, script, macros):
        self.script = script
        self.macros = macros

    def __str__(self):
        """Script's string representation"""
        description = self.script._description

        description = {
            k: v.format(self.macros)
            for k, v in description.items()
            }

        return _skeleton.format(descr=description)


# --Loading and saving Slurm batch scripts-------------------------------------
def load(filename):
    """Load Slurm batch script from disk.

    Load Slurm batch script from disk based on Python's simple
    configuration language:

    .. code-block:: ini

        [options]
        ntasks = 1

        [executable]
        command = echo
        arguments = 'Hello World!'
        transfer_executable = False

    Input and output files for the transfer mechanism can be listed in
    the sections ``transfer_input_files`` and ``transfer_output_files``,
    respectively. The ``command`` option in the ``executable`` section
    is the only mandatory one.

    Parameters
    ----------
    filename : str
        Path to saved Slurm batch script

    Returns
    -------
    SBatchScript
        Slurm batch script

    Notes
    -----
    The extended interpolation feature of Python's simple configuration
    language is enabled.

    """
    description = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation(),
        allow_no_value=True)

    description.read(filename)

    script = SBatchScript(
        executable=description["executable"]["command"],
        arguments=description["executable"].get("arguments", ""))

    script.transfer_executable = description["executable"].getboolean(
        "transfer_executable", False)

    if "options" in description:
        script.options.update(description["options"])

    if "transfer_input_files" in description:
        script.transfer_input_files.extend(
            description["transfer_input_files"])

    if "transfer_output_files" in description:
        script.transfer_output_files.extend(
            description["transfer_output_files"])

    return script


def save(script, filename):
    """Save Slurm batch script to disk.

    Save Slurm batch script to disk based on Python's simple
    configuration language.

    Parameters
    ----------
    script : SBatchScript
        Slurm batch script
    filename : str
        Path to output file

    """
    description = configparser.ConfigParser(allow_no_value=True)

    description["executable"] = {
        "command": script.executable,
        "arguments": script.arguments,
        "transfer_executable": script.transfer_executable
        }

    if len(script.options) > 0:
        description["options"] = script.options

    if len(script.transfer_input_files) > 0:
        description["transfer_input_files"] = {
            f: None for f in script.transfer_input_files
            }

    if len(script.transfer_output_files) > 0:
        description["transfer_output_files"] = {
            f: None for f in script.transfer_output_files
            }

    with open(filename, "w") as stream:
        description.write(stream)


# ---Batch script skeleton-----------------------------------------------------
_skeleton = """#!/usr/bin/env bash

{descr[options]}

echo "Working on node `hostname`."

echo 'Create working directory:'
workdir="slurm_job_$SLURM_JOB_NAME"
mkdir -v $workdir
cd $workdir

executable={descr[executable]}
transfer_executable={descr[transfer_executable]}

if [ "$transfer_executable" = "true" ]
then
    echo 'Transfer executable to node:'
    cp -v $executable .
    executable=./`basename $executable`
fi

inputfiles=({descr[transfer_input_files]})

echo 'Transfer input files to node:'
for inputfile in ${{inputfiles[*]}}
do
    cp -v $inputfile .
done

echo 'Execute...'
$executable {descr[arguments]}

outputfiles=({descr[transfer_output_files}])

echo 'Transfer output files:'
for outputfile in ${{outputfiles[*]}}
do
    mv -v `basename $outputfile` $outputfile
done

echo 'Remove working directory:'
cd ..
rm -rv $workdir"""
