# -*- coding: utf-8 -*-

"""Module containing a class for submitting Slurm batch scripts

"""
import configparser
import os
import re
import subprocess
import tempfile
import time

from . import sbatchscript


# ---Submitting Slurm batch scripts--------------------------------------------
class SBatch:
    """Slurm batch script submitter

    This class allows the successive submission of a collection of
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
            Mapping of job names to Slurm batch scripts
        partition : str, optional
            Partition for resource allocation

        Returns
        -------
        dict(str, int)
            Failed jobs; mapping of job names to job IDs

        """
        userid = str(os.getuid())
        scripts = dict(scripts)

        running = {}
        failed = {}

        # Successively submit jobs.
        while len(scripts) > 0:
            nnew = min(self.nmax - self.njobs(userid, partition), len(scripts))

            if nnew > 0:
                # We can submit new jobs. This means some jobs are done. Let's
                # check their status.
                failed.update(self._status(running))

            for _ in range(nnew):
                name, script = scripts.popitem()
                running[name] = self.submit(script, partition)

            time.sleep(self.wait)

        # Wait for all jobs to finish.
        while len(running) > 0:
            failed.update(self._status(running))
            time.sleep(self.wait)

        return failed

    def _status(self, jobs):
        """Job status

        Check the status of the given Slurm jobs, remove the completed
        ones, and return the failed ones.

        Parameters
        ----------
        jobs : dict(str, int)
            Jobs; mapping of job names to job IDs.

        Returns
        -------
        dict(str, int)
            Failed jobs; mapping of job names to job IDs

        """
        failed = {}
        for name, jobid in list(jobs.items()):
            status = self.status(jobid)

            if status != "RUNNING":
                jobs.pop(name)

            if status == "FAILED":
                failed[name] = jobid

        return failed

    @staticmethod
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
            Job ID

        Returns
        -------
        str
            Job status: 'RUNNING', 'SUCCESS', or 'FAILED'

        """
        process = subprocess.run(
            ["sacct", "-j", str(jobid), "-o", "state", "-n"],
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
