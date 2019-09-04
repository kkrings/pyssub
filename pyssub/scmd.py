# -*- coding: utf-8 -*-

"""Module containing functions wrapping Slurm commands

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
        "prefix": "pyssub_",
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
    are not equal to ``COMPLETED``.

    Parameters
    ----------
    jobs : dict(str, int)
        Mapping of job names to job IDs

    Returns
    -------
    dict(str, int)
        Mapping of names to IDs of the jobs that have failed

    """
    jobids = ["{}.batch".format(jobid) for jobid in jobs.values()]
    width = max(len(jobid) for jobid in jobids)

    # Check for completed jobs in chunks of 1000 job IDs. Otherwise, sacct
    # could fail if the string of comma-separated job IDs is too long.
    completed = []
    for start in range(0, len(jobids), 1000):
        select = slice(start, start+1000)

        command = [
            "sacct", "-j", ",".join(jobids[select]), "-n",
            "-o", "jobid%+{width},state%+9".format(width=width)
            ]

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8")

        completed.extend(line.split() for line in process.stdout.splitlines())

    pattern = re.compile(r"(?P<jobid>\d+).batch")

    failed = [
        int(pattern.match(jobid).group("jobid"))
        for jobid, state in completed
        if state != "COMPLETED"
        ]

    failed = {
        jobname: jobid for jobname, jobid in jobs.items()
        if jobid in failed
        }

    return failed
