# -*- coding: utf-8 -*-

"""Unit tests for `scmd` module.

"""
import unittest
import unittest.mock

import pyssub.sbatch
import pyssub.scmd


class TestSubmit(unittest.TestCase):
    """Test case for functions wrapping Slurm commands

    Test `pyssub.scmd.submit`. This function calls ``sbatch`` in a
    separate process via `subprocess.run`. This call will be mocked.

    """
    def test_jobid(self):
        """Test returned job ID.

        """
        reference = 123456
        jobid = self.run_cmd(reference)[0]
        message = "The job ID {} is not equal {}.".format(jobid, reference)
        self.assertEqual(jobid, reference, message)

    def test_with_partition(self):
        """Test ``sbatch`` options if a partition is given.

        """
        partition = "Some partition"
        command = self.run_cmd(jobid=123456, partition=partition)[1]
        message = "Command sbatch was not called with expected options."
        self.assertEqual(command[:-1], ["sbatch", "-p", partition], message)

    def run_cmd(self, jobid, partition=None):
        """Execute `submit`.

        Parameters
        ----------
        jobid : int
            Mock job ID
        partition : str, optional
            Partition name; will be passed to `submit`

        Returns
        -------
        jobid : int
            Job ID returned by `submit`
        command : tuple(str)
            Command mock `run` was called with

        """
        script = pyssub.sbatch.SBatchScript("test_executable.py")

        with unittest.mock.patch("subprocess.run") as mock:
            process = mock.return_value
            process.stdout = "Submitted batch job {}".format(jobid)
            jobid = pyssub.scmd.submit(script, partition)
            command = mock.call_args[0][0]

        return jobid, command


class TestNumJobs(unittest.TestCase):
    """Test case for functions wrapping Slurm commands

    Test `pyssub.scmd.numjobs`. This function calls ``squeue`` in a
    separate process via `subprocess.run`. This call will be mocked.

    """
    def test_num_jobs(self):
        """Test returned number of queuing jobs.

        """
        jobids = list(range(100))
        njobs = self.run_cmd(jobids, user="some user")[0]

        nref = len(jobids)
        message = "Number of jobs {} is not equal {}.".format(njobs, nref)

        self.assertEqual(njobs, nref, message)

    def test_with_partition(self):
        """Test ``squeue`` options if a partition is given.

        """
        user = "Some user"
        partition = "Some partition"
        command = self.run_cmd(range(100), user, partition)[1]
        message = "Command squeue was not called with expected options."
        # Ignore all previous options.
        self.assertEqual(command[-4:], ["-u", user, "-p", partition], message)

    def run_cmd(self, jobids, user, partition=None):
        """Execute `numjobs`.

        Parameters
        ----------
        jobids : list(int)
            Mock sequence of queuing jobs
        partition : str, optional
            Partition name; will be passed to `numjobs`

        Returns
        -------
        num : int
            Number of queuing jobs returned by `numjobs`
        command : tuple(str)
            Command mock `run` was called with

        """
        with unittest.mock.patch("subprocess.run") as mock:
            process = mock.return_value
            process.stdout = "\n".join("'{}'".format(iD) for iD in jobids)
            numjobs = pyssub.scmd.numjobs(user, partition)
            command = mock.call_args[0][0]

        return numjobs, command


class TestFailed(unittest.TestCase):
    """Test case for functions wrapping Slurm commands

    Test `pyssub.scmd.failed`. This function calls ``sacct`` in a
    separate process via `subprocess.run`. This call will be mocked.

    """
    def test_failed_jobs(self):
        """Test failed jobs.

        """
        reference = {
            "test_job_{:04d}".format(i): 123456 + i for i in range(10)
            }

        states = [
            "{iD}.batch {state:>9} ".format(iD=iD, state="FAILED")
            for iD in reference.values()
            ]

        completed = {
            "test_job_{:04d}".format(10 + i): 123466 + i for i in range(10)
            }

        states.extend(
            "{}.batch COMPLETED ".format(iD) for iD in completed.values())

        finished = dict(reference)
        finished.update(completed)

        with unittest.mock.patch("subprocess.run") as mock:
            process = mock.return_value
            process.stdout = "\n".join(states)
            failed = pyssub.scmd.failed(finished)

        message = "Reference failed jobs were not found."
        self.assertEqual(failed, reference, message)
