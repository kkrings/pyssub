#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for `sbatch` module.

"""
import json
import os
import pkg_resources
import shutil
import subprocess
import tempfile
import unittest

import pysdag.sbatch


# ---Helper class for executing batch script-----------------------------------
class Executable:
    """Test executable

    This helper class allows to locally execute a test executable via a
    batch script from inside the given working directory. The test
    executable takes a test input file, optionally writes a test output
    file, or optionally raises an exception. Test executable, test
    input, and test output file are transfered between the given working
    directory and the batch script's working directory. This way both a
    successful execution and different typical causes of failure can be
    tested via the test cases defined in this module.

    Parameters
    ----------
    copy_executable : bool, optional
        If `True` copy test executable to working directory. If set
        to `False`, a non-existing executable can be simulated.
    write_input : bool, optional
        If `True` write test input file to working directory. If set
        to `False`, a non-existing input file can be simulated.

    Attributes
    ----------
    workdir : str
        Path to working directory
    executable : str
        Path to text executable
    inputfile : str
        Path to test input file
    outputfile : str
        Path to test output file

    """
    # Path to test executable
    path = pkg_resources.resource_filename(__name__, "test_executable.py")

    def __init__(self, workdir, copy_executable=True, write_input=True):
        self.workdir = workdir

        self.executable = os.path.join(workdir, os.path.basename(self.path))
        if copy_executable:
            shutil.copy(self.path, self.executable)

        self.inputfile = os.path.join(workdir, "test_input.txt")
        if write_input:
            with open(self.inputfile, "w") as stream:
                stream.write("This is a test input file for PySDAG.\n")

        self.outputfile = os.path.join(workdir, "test_output.txt")

    def __call__(self, write_output=True, fail=False):
        """Create and execute batch script.

        Parameters
        ----------
        write_output : bool, optional
            If `True` write test output file to batch script's working
            directory. If set to `False`, a non-existing output file can
            be simulated.
        fail : bool, optional
            Simulate a failing executable.

        Returns
        -------
        CompletedProcess
            Execution result; it captures the batch script's return
            code and its output to both `stdout` and `stderr`.

        """
        arguments = "--in {}".format(os.path.basename(self.inputfile))

        if write_output:
            arguments += " --out {}".format(os.path.basename(self.outputfile))

        if fail:
            arguments += " --fail"

        macros = {
            "inputfile": self.inputfile,
            "outputfile": self.outputfile
            }

        script = pysdag.sbatch.SBatchScriptMacro(
            script=pysdag.sbatch.SBatchScript(self.executable, arguments),
            macros=macros)

        script.script.transfer_executable = True
        script.script.transfer_input_files.append("{macros[inputfile]}")
        script.script.transfer_output_files.append("{macros[outputfile]}")

        scriptfile = os.path.join(self.workdir, "test_executable.sh")

        with open(scriptfile, "w") as stream:
            stream.write(str(script))

        process = subprocess.run(
            ["bash", scriptfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.workdir,
            check=False,
            encoding="utf-8")

        return process


# ---Base class for batch script test cases------------------------------------
class TestSBatchScript:
    """Base class for batch script test cases

    This is a base class for implementing test cases that locally
    execute a test executable via a batch script, by using
    the `Executable` class, and check the batch script's return code and
    the proper cleanup of its working.  Derived class must provide the
    class attributes `workdir` and `returncode`.

    """
    @classmethod
    def tearDownClass(cls):
        cls.workdir.cleanup()

    def test_return_code(self):
        """Test for expected return code.

        """
        message = "Return code {} does not match expectation {}.".format(
            self.process.returncode, self.returncode)

        self.assertEqual(self.process.returncode, self.returncode, message)

    def test_cleanup(self):
        """Test for proper cleanup of working directory.

        """
        workdir = os.path.join(self.workdir.name, "slurm")
        message = "Working directory {} was not removed.".format(workdir)
        self.assertFalse(os.path.exists(workdir), message)


# ---Test case for successful batch script-------------------------------------
class TestSBatchScriptSuccess(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the batch script's execution was successful, a return code of
    zero is expected and a test output file should exist.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pysdag_")
        execute = Executable(cls.workdir.name)
        cls.outputfile = execute.outputfile
        cls.process = execute()
        cls.returncode = 0

    def test_output_file(self):
        """Test for existing test output file.

        """
        message = "Output file {} does not exist.".format(self.outputfile)
        self.assertTrue(os.path.exists(self.outputfile), message)


# ---Test cases for failed batch scripts---------------------------------------
class TestSBatchScriptFailureNoInputFile(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the test input file cannot be transfered because it does not
    exist, a return code of one is expected.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pysdag_")
        # Specify an input file that does not exist.
        cls.process = Executable(cls.workdir.name, write_input=False)()
        cls.returncode = 1


class TestSBatchScriptFailureNoExecutable(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the test executable cannot be transfered because it does not
    exist, a return code of one is expected.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pysdag_")
        cls.process = Executable(cls.workdir.name, copy_executable=False)()
        cls.returncode = 1


class TestSBatchScriptFailureExecutable(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the test executable fails, a return code of one is expected.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pysdag_")
        cls.process = Executable(cls.workdir.name)(fail=True)
        cls.returncode = 1


class TestSBatchScriptFailureNoOutputFile(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the test output file cannot be transfered because it does not
    exist, a return code of one is expected.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pysdag_")
        cls.process = Executable(cls.workdir.name)(write_output=False)
        cls.returncode = 1


# ---Test cases for saving and loading batch scripts---------------------------
class TestSBatchIO(unittest.TestCase):
    """Test case for saving and loading batch scripts

    Initialize a batch script, save it to disk, both directly and via a
    batch script collection, load it again, and check both scripts for
    equality.

    """
    @classmethod
    def setUpClass(cls):
        cls.script = pysdag.sbatch.SBatchScript(
            executable="/path/to/test_executable.py",
            arguments="--in test_input_0000.txt")

        cls.script.transfer_executable = True

        cls.script.transfer_input_files.append(
            "/path/to/test_input_0000.txt")

        cls.script.transfer_output_files.append(
            "/path/to/test_output_0000.txt")

    def test_save_and_load(self):
        """Save script directly and test for equality.

        """
        with tempfile.TemporaryDirectory(prefix="pysdag_") as dirname:
            filename = os.path.join(dirname, "script.json")
            pysdag.sbatch.save(self.script, filename)
            other = pysdag.sbatch.load(filename)

        self.assertEqual(self.script, other)

    def test_collection(self):
        """Save script via collection and test for equality.

        """
        script = pysdag.sbatch.SBatchScript(
            executable="/path/to/test_executable.py",
            arguments="--in test_input_{macros[jobid]:04d}.txt")

        script.transfer_executable = True

        script.transfer_input_files.append(
            "/path/to/test_input_{macros[jobid]:04d}.txt")

        script.transfer_output_files.append(
            "/path/to/test_output_{macros[jobid]:04d}.txt")

        name = "test_job"
        with tempfile.TemporaryDirectory(prefix="pysdag_") as dirname:
            scriptfile = os.path.join(dirname, "script.json")
            pysdag.sbatch.save(script, scriptfile)

            collection = [{
                "name": name,
                "script": scriptfile,
                "macros": {"jobid": 0}
                }]

            filename = os.path.join(dirname, "collection.json")
            with open(filename, "w") as stream:
                json.dump(collection, stream)

            collection = pysdag.sbatch.collection(filename)

        self.assertEqual(collection, {name: self.script})


if __name__ == "__main__":
    # Run unit test.
    unittest.main()
