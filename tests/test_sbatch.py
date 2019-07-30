#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for sbatch module.

"""
import os
import pkg_resources
import subprocess
import tempfile
import unittest

import pyslurm.sbatch


class TestSBatchScriptMacro(unittest.TestCase):
    """Test case for sbatch module

    Execute the test executable locally within a batch script; test for
    a return code of zero, an existing output file, and a proper cleanup
    of the working directory.

    """
    @classmethod
    def setUpClass(cls):
        # Create temporary working directory.
        cls.workdir = tempfile.TemporaryDirectory(prefix="pyslurm_")

        # Create test input file.
        inputfile = os.path.join(cls.workdir.name, "test_input.txt")

        with open(inputfile, "w") as stream:
            stream.write("This is a test input file for PySlurm.\n")

        # Create batch script.
        executable = pkg_resources.resource_filename(
            __name__, os.path.join("data", "executable.py"))

        script = pyslurm.sbatch.SBatchScript(
            executable, arguments="--in test_input.txt --out test_output.txt")

        script.transfer_executable = True
        script.transfer_input_files.append("{macros[inputfile]}")
        script.transfer_output_files.append("{macros[outputfile]}")

        cls.outputfile = os.path.join(cls.workdir.name, "test_output.txt")

        macros = {
            "inputfile": inputfile,
            "outputfile": cls.outputfile
            }

        script = pyslurm.sbatch.SBatchScriptMacro(script, macros)
        scriptfile = os.path.join(cls.workdir.name, "test_executable.sh")

        with open(scriptfile, "w") as stream:
            stream.write(str(script))

        # Execute batch script
        cls.process = subprocess.run(
            ["bash", scriptfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cls.workdir.name,
            check=False,
            encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        # Remove temporary working directory.
        cls.workdir.cleanup()

    def test_return_code(self):
        """Test for return code of zero.

        """
        message = "Batch script failed with return code {}: {}.".format(
            self.process.returncode, self.process.stderr)

        self.assertEqual(self.process.returncode, 0, message)

    def test_output_file(self):
        """Test for existing output file.

        """
        message = "Output file {} does not exist.".format(self.outputfile)
        self.assertTrue(os.path.exists(self.outputfile), message)

    def test_cleanup(self):
        """Test for proper cleanup of working directory.

        """
        workdir = os.path.join(self.workdir.name, "slurm")
        message = "Working directory {} was not removed.".format(workdir)
        self.assertFalse(os.path.exists(workdir), message)


if __name__ == "__main__":
    # Run unit test.
    unittest.main()
