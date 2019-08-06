# -*- coding: utf-8 -*-

"""Unit tests for `shist` module

"""
import os
import tempfile
import unittest

import pyssub.shist


class TestSHist(unittest.TestCase):
    """Test case for Slurm job history

    Generate an arbitrary mapping of job names to job IDs, save it to
    disk, load it again, and check for equality.

    """
    def test_shist(self):
        """Test Slurm job history.

        """
        jobs = {
            "test_job_{0:03d}".format(i): 123456 + i
            for i in range(100)
            }

        with tempfile.TemporaryDirectory(prefix="pyssub_") as dirname:
            filename = os.path.join(dirname, "jobs.txt")
            pyssub.shist.save(filename, jobs)
            other = pyssub.shist.load(filename)

        message = (
            "Mapping of job names to job IDs is not the same after being "
            "saved to disk and loaded from disk again."
            )

        self.assertEqual(jobs, other, message)

    def test_shist_empty(self):
        """Test empty Slurm job history.

        """
        with tempfile.TemporaryDirectory(prefix="pyssub_") as dirname:
            filename = os.path.join(dirname, "jobs.txt")
            pyssub.shist.save(filename, {})
            jobs = pyssub.shist.load(filename)

        message = (
            "After saving an empty job history to disk and loading it again, "
            "the returned history is not empty."
            )

        self.assertEqual(len(jobs), 0, message)
