# -*- coding: utf-8 -*-

"""Unit tests for `sbatch` module

"""
import json
import os
import pkg_resources
import shutil
import subprocess
import tempfile
import unittest

import pyssub.sbatch


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
                stream.write("This is a test input file for pyssub.\n")

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

        script = pyssub.sbatch.SBatchScript(self.executable, arguments)

        script.transfer_executable = True
        script.transfer_input_files.append(self.inputfile)
        script.transfer_output_files.append(self.outputfile)

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
        cls.workdir = tempfile.TemporaryDirectory(prefix="pyssub_")
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
        cls.workdir = tempfile.TemporaryDirectory(prefix="pyssub_")
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
        cls.workdir = tempfile.TemporaryDirectory(prefix="pyssub_")
        cls.process = Executable(cls.workdir.name, copy_executable=False)()
        cls.returncode = 1


class TestSBatchScriptFailureExecutable(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the test executable fails, a return code of one is expected.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pyssub_")
        cls.process = Executable(cls.workdir.name)(fail=True)
        cls.returncode = 1


class TestSBatchScriptFailureNoOutputFile(unittest.TestCase, TestSBatchScript):
    """Test case for batch script

    If the test output file cannot be transfered because it does not
    exist, a return code of one is expected.

    """
    @classmethod
    def setUpClass(cls):
        cls.workdir = tempfile.TemporaryDirectory(prefix="pyssub_")
        cls.process = Executable(cls.workdir.name)(write_output=False)
        cls.returncode = 1


# ---Test case for batch script containing macros------------------------------
class TestSBatchScriptMacro(unittest.TestCase):
    """Test case for batch script containing macros

    Create two scripts, one with and the other without macros. Specify
    macro values that correspond to the script without macros and test
    for scripts for equality.

    """
    def test_equality(self):
        """Test scripts for equality.

        """
        # Batch script without macros.
        script = pyssub.sbatch.SBatchScript(
            executable="test_executable.py",
            arguments="--in test_input_00.txt")

        script.options["job-name"] = "test_00"

        script.transfer_executable = True
        script.transfer_input_files.append("test_input_00.txt")
        script.transfer_output_files.append("test_output_00.txt")

        # Same batch script with macros.
        skeleton = pyssub.sbatch.SBatchScript(
            executable="test_executable.py",
            arguments="--in test_input_{macros[jobid]:02d}.txt")

        skeleton.options["job-name"] = "test_{macros[jobid]:02d}"

        skeleton.transfer_executable = True

        skeleton.transfer_input_files.append(
            "test_input_{macros[jobid]:02d}.txt")

        skeleton.transfer_output_files.append(
            "test_output_{macros[jobid]:02d}.txt")

        other = pyssub.sbatch.SBatchScriptMacro(
            script=skeleton, macros={"jobid": 0})

        message = "The two Slurm batch scripts are not equal."
        self.assertEqual(script, other, message)


# ---Test cases for batch scripts' JSON support--------------------------------
class TestSBatchScriptJSON(unittest.TestCase):
    """Test case for JSON-encoding and decoding batch scripts

    Initialize a batch script, save it to disk, load it again, and check
    for equality.

    """
    def setUp(self):
        """Initialize batch script.

        """
        self.script = pyssub.sbatch.SBatchScript("test_executable.py")

    def run_test(self, script):
        """Execute test case.

        """
        with tempfile.TemporaryDirectory(prefix="pyssub_") as dirname:
            filename = os.path.join(dirname, "script.json")

            with open(filename, "w") as stream:
                json.dump(
                    script, stream,
                    cls=pyssub.sbatch.SBatchScriptEncoder)

            with open(filename, "r") as stream:
                other = json.load(
                    stream, object_hook=pyssub.sbatch.SBatchScriptDecoder())

        message = "Batch script is not the same after saving and loading."
        self.assertEqual(other, script, message)

    def test_default(self):
        """Test with only the executable specified.

        """
        self.run_test(self.script)

    def test_with_arguments(self):
        """Test with arguments specified.

        """
        self.script.arguments = "--in test_input.txt"
        self.run_test(self.script)

    def test_with_options(self):
        """Test with Slurm options specified.

        """
        self.script.options["ntasks"] = 1
        self.run_test(self.script)

    def test_with_transfer_input_files(self):
        """Test with input files specified for transfer.

        """
        self.script.transfer_input_files.append("test_input.txt")
        self.run_test(self.script)

    def test_with_transfer_output_files(self):
        """Test with output files specified for transfer.

        """
        self.script.transfer_output_files.append("test_output.txt")
        self.run_test(self.script)

    def test_with_macros(self):
        """Test with macro support.

        """
        self.script.arguments = "--in test_input_{macros[jobid]:02d}.txt"

        script = pyssub.sbatch.SBatchScriptMacro(
            self.script, macros={"jobid": 0})

        self.run_test(script)


class TestSBatchScriptEncoderException(unittest.TestCase):
    """Test case for batch script encoder

    Check if a `TypeError` is raised if an object of unknown type is
    given to the batch script encoder.

    """
    def test_exception(self):
        """Test for `TypeError`.

        """
        class DummyType:
            """Some dummy class that JSON cannot encode."""

        message = "Expect TypeError if an object of unkown type is given."

        with self.assertRaises(TypeError, msg=message):
            with tempfile.TemporaryDirectory(prefix="pyssub_") as dirname:
                filename = os.path.join(dirname, "script.json")

                with open(filename, "w") as stream:
                    json.dump(
                        DummyType(), stream,
                        cls=pyssub.sbatch.SBatchScriptEncoder)


class TestSBatchScriptCollection(unittest.TestCase):
    """Test case for batch script collection

    Initialize both a collection of batch scripts and a corresponding
    JSON object, save the JSON object to disk, load it again using the
    custom JSON decoder for batch scripts, and test both the original
    collection and the decoded collection for equality.

    """
    def test_equality(self):
        """Test batch script collections for equality.

        """
        skeleton = pyssub.sbatch.SBatchScript(
            executable="test_executable.py",
            arguments="--in test_input_{macros[jobid]:03d}.txt")

        skeleton.transfer_executable = True

        skeleton.transfer_input_files.append(
            "test_input_{macros[jobid]:03d}.txt")

        skeleton.transfer_output_files.append(
            "test_output_{macros[jobid]:03d}.txt")

        scripts = {}
        for jobid in range(100):
            script = pyssub.sbatch.SBatchScriptMacro(
                skeleton, macros={"jobid": jobid})

            scripts["test_job_{:03d}".format(jobid)] = script

        with tempfile.TemporaryDirectory(prefix="pyssub_") as dirname:
            scriptfile = os.path.join(dirname, "script.json")

            with open(scriptfile, "w") as stream:
                json.dump(
                    skeleton, stream,
                    cls=pyssub.sbatch.SBatchScriptEncoder)

            collection = {}
            for name, script in scripts.items():
                collection[name] = {
                    "name": name,
                    "script": scriptfile,
                    "macros": script.macros
                    }

            filename = os.path.join(dirname, "collection.json")

            with open(filename, "w") as stream:
                json.dump(collection, stream)

            with open(filename, "r") as stream:
                other = json.load(
                    stream, object_hook=pyssub.sbatch.SBatchScriptDecoder())

        message = "The two batch script collections are not equal."
        self.assertEqual(scripts, other, message)
