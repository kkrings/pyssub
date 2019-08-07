#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create a collection of Slurm batch scripts for executing an executable
on a Slurm cluster. Each job has the macros job name ``jobname``, and
job ID ``jobid``, which can be passed to the executable and/or the file
transfer mechanism.

"""
import json
import os

import pyssub.sbatch


def main(config, arguments=""):
    script = pyssub.sbatch.SBatchScript(config.executable, arguments)

    script.options.update({
        "job-name": "{macros[jobname]}",
        "time": "00:10:00",
        "chdir": "/var/tmp",
        "error": os.path.join(config.stdout, "{macros[jobname]}.out"),
        "output": os.path.join(config.stdout, "{macros[jobname]}.out")
        })

    script.transfer_executable = True
    script.transfer_input_files.extend(config.transfer_input_files)
    script.transfer_output_files.extend(config.transfer_output_files)

    scriptfile = config.name + ".script"
    with open(scriptfile, "w") as stream:
        json.dump(script, stream, cls=pyssub.sbatch.SBatchScriptEncoder)

    njobs = len(config.jobs)
    suffix = "_{{:0{width}d}}".format(width=len(str(njobs)))

    collection = {}
    for jobid in config.jobs:
        jobname = config.name + suffix.format(jobid)

        collection[jobname] = {
            "script": scriptfile,
            "macros": {
                "jobname": jobname,
                "jobid": jobid
                }
            }

    with open(config.name + ".jobs", "w") as stream:
        json.dump(collection, stream, cls=pyssub.sbatch.SBatchScriptEncoder)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Additional arguments are passed to the exectuable.")

    parser.add_argument(
        "--sbatch-name",
        nargs="?",
        type=str,
        help="jobs' prefix",
        required=True,
        dest="name")

    parser.add_argument(
        "--sbatch-exec",
        nargs="?",
        type=str,
        help="path to executable",
        required=True,
        metavar="PATH",
        dest="executable")

    parser.add_argument(
        "--sbatch-jobs",
        nargs="?",
        type=str,
        help="sequence of job IDs: ``%(default)s``",
        default="[1]",
        metavar="EXPR",
        dest="jobs")

    parser.add_argument(
        "--sbatch-stdout",
        nargs="?",
        type=str,
        help="path to stdout/stderr output directory: ``%(default)s``",
        default="/scratch9/kkrings/logs",
        metavar="PATH",
        dest="stdout")

    parser.add_argument(
        "--sbatch-in",
        nargs="+",
        type=str,
        help="transfer input files to node: ``None``",
        default=[],
        metavar="PATH",
        dest="transfer_input_files")

    parser.add_argument(
        "--sbatch-out",
        nargs="+",
        type=str,
        help="transfer output files from node: ``None``",
        default=[],
        metavar="PATH",
        dest="transfer_output_files")

    config, arguments = parser.parse_known_args()
    config.jobs = eval(config.jobs)

    main(config, arguments=" ".join(arguments))
