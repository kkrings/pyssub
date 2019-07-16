# -*- coding: utf-8 -*-

"""Module containing functions wrapping Slurm commands.

"""
import os
import re
import subprocess
import tempfile


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


def numjobs(user, partition=None):
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


def failed(jobs):
    """Failed jobs

    Check which of the given jobs have failed, meaning that their states
    are neither ``COMPLETED, RUNNING, or PENNDING``.

    Parameters
    ----------
    jobs : dict(str, int)
        Mapping of job names to job IDs

    Returns
    -------
    dict(str, int)
        Mapping of names to IDs of the jobs that have failed

    """
    jobids = ",".join(str(jobid) for jobid in jobs.values())

    command = ["sacct", "-j", jobids, "-n", "-o", "state"]

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        encoding="utf-8")

    states = [state.strip() for state in process.stdout.splitlines()]

    result = {
        name: jobid
        for (name, jobid), state in zip(jobs.items(), states)
        if state not in ["COMPLETED", "RUNNING", "PENDING"]
        }

    return result
