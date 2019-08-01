# -*- coding: utf-8 -*-

"""Module containing classes representing a Slurm batch script

"""
import json


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
        self.options = {}

        # File transfer mechanism
        self.transfer_executable = False
        self.transfer_input_files = []
        self.transfer_output_files = []

    def __str__(self):
        """Script's string representation"""
        return _skeleton.format(descr=self._description)

    def __eq__(self, other):
        """Compare to other script."""
        return str(self) == str(other)

    @property
    def _description(self):
        """dict(str, str): Script's description; will be inserted
        into `_skeleton` when script's string representation is called.
        """
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
            k: v.format(macros=self.macros)
            for k, v in description.items()
            }

        return _skeleton.format(descr=description)

    def __eq__(self, other):
        """Compare to other script."""
        return str(self) == str(other)


# ---Loading and saving Slurm batch script-------------------------------------
class SBatchScriptEncoder(json.JSONEncoder):
    """JSON encoder for Slurm batch script

    This class provides a JSON-compatible representation of a Slurm
    batch script.

    """
    def default(self, obj):
        """Try to encode the given object."""
        if isinstance(obj, SBatchScript):
            return self._encode(script=obj)
        else:
            return super().default(obj)

    def _encode(self, script):
        """Encode the given Slurm batch script."""
        description = {"executable": script.executable}

        if len(script.arguments) > 0:
            description["arguments"] = script.arguments

        description["transfer_executable"] = script.transfer_executable

        if len(script.options) > 0:
            description["options"] = {
                k: str(v) for k, v in script.options.items()
                }

        if len(script.transfer_input_files) > 0:
            description["transfer_input_files"] = script.transfer_input_files

        if len(script.transfer_output_files) > 0:
            description["transfer_output_files"] = script.transfer_output_files

        return description


def load(filename):
    """Load Slurm batch script from disk.

    Load Slurm batch script from disk based on the JSON format:

    .. code-block:: json

        {
            "executable": "command name or path to executable"
            "arguments": "arguments the executable takes"
            "transfer_executable": False
            "options": {
                "ntasks": 1
            }
            "transfer_input_files": [
                "path to 1st input file",
                "path to 2nd input file"
            ]
            "transfer_output_files": [
                "path to 1st output file",
                "path to 2nd output file"
            ]
        }

    The ``executable`` key is the only mandatory one.

    Parameters
    ----------
    filename : str
        Path to saved Slurm batch script

    Returns
    -------
    SBatchScript
        Slurm batch script

    """
    with open(filename, "r") as stream:
        description = json.load(stream)

    script = SBatchScript(
        executable=description["executable"],
        arguments=description.get("arguments", ""))

    script.transfer_executable = description.get("transfer_executable", False)

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

    Save Slurm batch script to disk based on the JSON format.

    Parameters
    ----------
    script : SBatchScript
        Slurm batch script
    filename : str
        Path to output file

    """
    with open(filename, "w") as stream:
        json.dump(script, stream, cls=SBatchScriptEncoder, indent=4)


# ---Loading of Slurm batch script collection----------------------------------
def collection(filename, rescue=None):
    """Load Slurm batch scripts from disk.

    Load collection of Slurm batch scripts from disk based on the JSON
    format:

    .. code-block:: json

        [
            {
                "name": "name of 1st job",
                "script": "path to saved Slurm batch script"
                "macros": {
                    "name of 1st macro": "value of 1st macro",
                    "name of 2nd macro": "value of 2nd macro"
                }
            }
            {
                "name": "name of 2nd job"
                "script": "path to saved Slurm batch script"
            }
        ]

    Parameters
    ----------
    filename : str
        Path to saved collection of Slurm batch scripts
    rescue : list(str), optional
        Sequence of names of jobs that should be taken into account; all
        others are ignored.

    Returns
    -------
    dict(str, SBatchScriptMacro)
        Mapping of job names to Slurm batch scripts

    """
    with open(filename, "r") as stream:
        descriptionlist = json.load(stream)

    scripts = {}
    for description in descriptionlist:
        name = description["name"]

        if rescue is not None and name not in rescue:
            continue

        scripts[name] = SBatchScriptMacro(
            script=load(description["script"]),
            macros=description["macros"])

    return scripts


# ---Batch script skeleton-----------------------------------------------------
_skeleton = """#!/usr/bin/env bash

{descr[options]}

echo "Working on node `hostname`."
echo "Current directory: `pwd`"

if [ -z $SLURM_JOB_ID ]
then
    workdir="slurm"
else
    workdir="slurm_$SLURM_JOB_ID"
fi

echo 'Create working directory:'
mkdir -v $workdir

status=$?
if [ $status -ne 0 ]
then
    exit $status
fi

function cleanup() {{
    echo 'Remove working directory:'
    cd ..
    rm -rv $workdir
}}

cd $workdir

executable={descr[executable]}
transfer_executable={descr[transfer_executable]}

if [ "$transfer_executable" = "true" ]
then
    echo 'Transfer executable to node:'
    cp -v $executable .

    status=$?
    if [ $status -ne 0 ]
    then
        cleanup
        exit $status
    fi

    executable=./`basename $executable`
fi

inputfiles=({descr[transfer_input_files]})

echo 'Transfer input files to node:'
status=0
for inputfile in ${{inputfiles[*]}}
do
    cp -v $inputfile .
    status+=$?
done

if [ $status -ne 0 ]
then
    cleanup
    exit $status
fi

echo 'Execute...'
$executable {descr[arguments]}

status=$?
if [ $status -ne 0 ]
then
    cleanup
    exit $status
fi

outputfiles=({descr[transfer_output_files]})

echo 'Transfer output files:'
status=0
for outputfile in ${{outputfiles[*]}}
do
    mv -v `basename $outputfile` $outputfile
    status+=$?
done

if [ $status -ne 0 ]
then
    cleanup
    exit $status
fi

cleanup"""
