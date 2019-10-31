# -*- coding: utf-8 -*-

"""Module containing functions wrapping Slurm commands

"""
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Optional

from .sbatch import SBatchScript


def submit(script: SBatchScript, partition: Optional[str] = None) -> int:
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

    Raises
    ------
    RuntimeError
        If job ID cannot be matched from `sbatch`'s output.

    """
    # Save script to disk.
    with tempfile.NamedTemporaryFile(
            mode="w",
            prefix="pyssub_",
            suffix=".sh",
            delete=False) as scriptfile:
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

    # Remove script from disk.
    os.remove(scriptfile.name)

    match = re.match(
        r"Submitted batch job (?P<jobid>\d+)",
        process.stdout)

    if match is None:
        raise RuntimeError(
            "Cannot match job ID from '{}'.".format(process.stdout))

    return int(match.group("jobid"))


def numjobs(user: str, partition: Optional[str] = None) -> int:
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


def failed(jobs: Dict[str, int]) -> Dict[str, int]:
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

    Raises
    ------
    RuntimeError
        If job ID cannot be matched from `sacct`'s output.

    """
    jobids = ["{}.batch".format(jobid) for jobid in jobs.values()]
    width = max(len(jobid) for jobid in jobids)

    # Check for completed jobs in chunks of 1000 job IDs. Otherwise, sacct
    # could fail if the string of comma-separated job IDs is too long.
    completed: List[List[str]] = []
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

    selected: List[int] = []
    for jobid, state in completed:
        if state != "COMPLETED":
            match = pattern.match(jobid)

            if match is None:
                raise RuntimeError(
                    "Cannot match job ID from '{}'.".format(jobid))

            selected.append(int(match.group("jobid")))

    failed = {
        jobname: jobid for jobname, jobid in jobs.items()
        if jobid in selected
        }

    return failed
