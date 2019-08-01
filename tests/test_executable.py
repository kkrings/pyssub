#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test executable for `pyssub`.

If no command-line arguments are provided, this script simulates the
successful execution of a command. A failed execution is simulated by
raising a runtime exception if the option fail is used. This script can
also be used to test the simple file transfer mechanism provided
by `pyssub` by either reading the content of the given input file or by
writing an output file.

"""


def main(inputfile=None, outputfile=None, fail=False):
    if fail:
        raise RuntimeError("Simulate a failed execution.")

    print("Simulate a successful execution.")

    if inputfile is not None:
        print("Read test input file.")

        with open(inputfile) as stream:
            print(stream.readlines()[0][:-1])

    if outputfile is not None:
        print("Write a test output file.")

        with open(outputfile, "w") as stream:
            stream.write("This is a test output file for pyssub.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--in",
        nargs="?",
        type=str,
        help="path to test input file",
        metavar="PATH",
        dest="inputfile")

    parser.add_argument(
        "--out",
        nargs="?",
        type=str,
        help="path to test output file",
        metavar="PATH",
        dest="outputfile")

    parser.add_argument(
        "--fail",
        help="raise a runtime exception",
        action="store_true",
        default=False)

    args = parser.parse_args()

    main(args.inputfile, args.outputfile, args.fail)
