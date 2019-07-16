# -*- coding: utf-8 -*-

"""Module containing a function for submitting Slurm batch scripts

"""
import configparser
import os
import re
import subprocess
import tempfile

from . import sbatchscript


# ---Submitting Slurm batch scripts--------------------------------------------
def submit(script, partition=None):
    """Submit Slurm batch script.

    Parameters
    ----------
    script : SBatchScript
        Slurm batch script
    partition : str, optional
        Partition for resource allocation

    Returns
    -------
    int
        Job ID

    """
    # Save script to disk.
    options = {
        "mode": "w",
        "prefix": "pyslurm_",
        "suffix": ".sh",
        "delete": False
        }

    with tempfile.NamedTemporaryFile(**options) as scriptfile:
        scriptfile.write(str(script))

    command = ["sbatch"]

    if partition is not None:
        command.extend(["-p", partition])

    command.append(scriptfile.name)

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        encoding="utf-8")

    match = re.match(
        r"Submitted batch job (?P<jobid>\d+)",
        process.stdout)

    # Remove script from disk.
    os.remove(scriptfile.name)

    return int(match.group("jobid"))


def njobs(user, partition=None):
    """Number of queuing jobs

    Check the number of queuing jobs for the given `user`
    and `partition`.

    Parameters
    ----------
    user : str
        User name or ID
    partition : str, optional
        Partition name

    Returns
    -------
    int
        Number of queuing jobs

    """
    command = ["squeue", "-h", "-o", "'%.i'", "-u", user]

    if partition is not None:
        command.extend(["-p", partition])

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        encoding="utf-8")

    return len(process.stdout.splitlines())


# --Loading Slurm batch scripts------------------------------------------------
def load(filename):
    """Load Slurm batch scripts from disk.

    Load collection of Slurm batch scripts from disk based on Python's
    simple configuration language:

    .. code-block:: ini

        [Name of 1st job]
        script = path to saved Slurm batch script

        # Macros are optional.
        name of 1st macro = value of 1st macro
        name of 2nd macro = value of 2nd macro

        [Name of 2nd job]
        script = path to saved Slurm batch script

    Parameters
    ----------
    filename : str
        Path to saved collection of Slurm batch scripts

    Returns
    -------
    dict(str, SBatchScriptMacro)
        Mapping of job names to Slurm batch scripts

    Notes
    -----
    The extended interpolation feature of Python's simple configuration
    language is enabled.

    """
    description = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())

    description.read(filename)

    scripts = {}
    for name in description.sections():
        macros = dict(description[name])
        script = sbatchscript.load(macros.pop("script"))
        scripts[name] = sbatchscript.SBatchScriptMacro(script, macros)

    return scripts


# --Save job names and IDs.----------------------------------------------------
def save(filename, jobs):
    """Save names and IDs of submitted Slurm jobs to disk.

    Parameters
    ----------
    filename : str
        Path to output file
    jobs : dict(str, int)
        Mapping of job names to job IDs

    """
    width = {
        "jobname": max(len(jobname) for jobname in jobs.keys()),
        "jobid": max(len(str(jobid)) for jobid in jobs.values())
        }

    width["jobname"] = max(width["jobname"], len("# Job name"))
    width["jobid"] = max(width["jobid"], len("job ID"))

    line = "{{:{width[jobname]}}} {{:{width[jobid]}}}\n".format(width=width)

    with open(filename, "w") as stream:
        stream.write(line.format("# Job name", "job ID"))

        for jobname, jobid in jobs.items():
            stream.write(line.format(jobname, jobid))
