# -*- coding: utf-8 -*-

"""Module containing a class for submitting Slurm batch scripts

"""
import os
import re
import subprocess
import tempfile
import time


class SBatch:
    """Slurm batch script submitter

    This class allows the successive submission of a sequence of batch
    scripts into the Slurm queue, checking that not more jobs
    than `nmax` are queuing.

    Attributes
    ----------
    nmax : int
        Maximum allowed number of queuing jobs
    wait : int
        Number of seconds before next submission

    """
    def __init__(self, nmax=1000, wait=120):
        self.nmax = nmax
        self.wait = wait

    def __call__(self, scripts, partition=None):
        """Successively submit Slurm batch scripts.

        Parameters
        ----------
        scripts : dict(str, SBatchScript)
            Mapping of job names to batch scripts
        partition : str, optional
            Partition for resource allocation

        """
        userid = str(os.getuid())

        scripts = dict(scripts)
        jobids = {}

        while len(scripts) > 0:
            nnew = self.nmax - self.njobs(userid, partition)

            for _ in range(nnew):
                name, script = scripts.popitem()
                jobids[name] = self.submit(script, partition)

            time.sleep(self.wait)

        return jobids

    @staticmethod
    def submit(script, partition=None):
        """Submit Slurm batch script.

        Parameters
        ----------
        script : Script
            Batch script
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
            scriptfile.write(script)

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

    @staticmethod
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
        command = ["squeue", "-h", "-u", user]

        if partition is not None:
            command.extend(["-p", partition])

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8")

        return len(process.stdout.splitlines())

    @staticmethod
    def status(jobid):
        """Job status

        Check the status of the given Slurm job.

        Parameters
        ----------
        jobid : int
            Slurm job ID

        Returns
        -------
        str
            Job status: 'RUNNING', 'SUCCESS', or 'FAILED'

        """
        process = subprocess.run(
            ["sacct", "-j", jobid, "-o", "state", "-n"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8")

        status = process.stdout.splitlines()[0].strip()

        if status == "RUNNING":
            return status

        if status == "COMPLETED":
            return "SUCCESS"

        return "FAILED"
