# -*- coding: utf-8 -*-

"""Module containing classes representing a Slurm batch script and
corresponding JSON encoder and decoder

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
        Mapping of sbatch options to objects (string-) representing
        values
    transfer_executable : bool
        Transfer `executable` to node.
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
        string representation is called

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


# ---JSON support for Slurm batch script---------------------------------------
class SBatchScriptEncoder(json.JSONEncoder):
    """JSON encoder for Slurm batch script

    This class provides a JSON-compatible representation of a Slurm
    batch script; both `SBatchScript` and `SBatchScriptMacro` are
    supported.

    """
    def default(self, o):
        """Try to encode the given object."""
        if isinstance(o, SBatchScript):
            return self._encode(o)

        if isinstance(o, SBatchScriptMacro):
            return {"script": self._encode(o.script), "macros": o.macros}

        return super().default(o)

    def _encode(self, script):
        """Encode Slurm batch script.

        Parameters
        ----------
        script : SBatchScript
            Slurm batch script

        Returns
        -------
        dict
            Script's JSON-compatible representation

        """
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


class SBatchScriptDecoder:
    """JSON decoder for Slurm batch script

    This callable class can be used as an `object_hook` when loading a
    JSON object from disk. All objects that represent a Slurm batch
    script, with or without macros, are decoded into the corresponding
    Python type.

    """
    def __call__(self, jsonobject):
        """Try to decode the given JSON object.

        If the object contains ``script``, `decode_macro` is called. If
        the object contains ``executable``, `decode` is called.
        Otherwise, the object is untouched.

        Parameters
        ----------
        jsonobject : dict
            JSON object

        Returns
        -------
        Either decoded JSON object or JSON object itself

        """
        if "script" in jsonobject:
            return self.decode_macro(description=jsonobject)

        if "executable" in jsonobject:
            return self.decode(description=jsonobject)

        return jsonobject

    def decode(self, description):
        """Decode Slurm batch script.

        Parameters
        ----------
        description : dict
            Script's JSON-compatible representation

        Returns
        -------
        SBatchScript
            Slurm batch script

        """
        script = SBatchScript(
            executable=description["executable"],
            arguments=description.get("arguments", ""))

        script.transfer_executable = description.get(
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

    def decode_macro(self, description):
        """Decode Slurm batch script containing macros.

        If ``script`` points to a string, it is interpreted as a path to
        a JSON-encoded Slurm batch script on disk that will be loaded
        and decoded.

        Parameters
        ----------
        description : dict
            Script's JSON-compatible representation

        Returns
        -------
        SBatchScriptMacro
            Slurm batch script

        """
        script = description["script"]

        if isinstance(script, str):
            with open(script, "r") as stream:
                script = self.decode(json.load(stream))

        return SBatchScriptMacro(script, macros=description["macros"])


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
