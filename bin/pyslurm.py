#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Successively submit batch scripts into the Slurm queue, checking that
not more jobs than `nmax` are queuing.

"""
import configparser

import pyslurm.script
import pyslurm.submit


def main(inputfile, nmax=1000, wait=120, partition=None):
    submitter = pyslurm.submit.SBatch(nmax, wait)

    # Load Slurm batch scripts from disk.
    config = configparser.ConfigParser()
    config.read(inputfile)

    # Submit Slurm batch scripts.
    scripts = dict(pyslurm.script.SBatchScriptDict(config))
    submitter.run(scripts, partition)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--in",
        nargs="?",
        type=str,
        help="path to submit description",
        required=True,
        metavar="PATH",
        dest="inputfile")

    parser.add_argument(
        "--nmax",
        nargs="?",
        type=int,
        help="maximum allowed number of queuing jobs (%(default)s)",
        default=1000,
        metavar="NUM")

    parser.add_argument(
        "--wait",
        nargs="?",
        type=int,
        help="number of seconds before next submission (%(default)s)",
        default=120,
        metavar="SEC")

    parser.add_argument(
        "--partition",
        nargs="?",
        type=str,
        help="request this particular partition",
        default=None,
        metavar="NAME")

    args = parser.parse_args()

    main(args.inputfile, args.nmax, args.wait, args.partition)
