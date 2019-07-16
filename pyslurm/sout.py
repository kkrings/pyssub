# -*- coding: utf-8 -*-

"""Module containing functions for saving/loading the names and IDs of
submitted Slurm jobs

"""


def load(filename):
    """Load Slurm jobs from disk.

    Load names and IDs of submitted Slurm jobs from disk.

    Parameters
    ----------
    filename : str
        Path to input file

    Returns
    -------
    dict(str, int)
        Mapping of job names to job IDs

    """
    with open(filename) as stream:
        rows = stream.readlines()

    jobnames = [
        row.split()[0]
        for row in rows if not row.startswith("#")
        ]

    jobids = [
        int(row.split()[1])
        for row in rows if not row.startswith("#")
        ]

    return dict(zip(jobnames, jobids))


def save(filename, jobs):
    """Save Slurm jobs to disk.

    Save names and IDs of submitted Slurm jobs to disk.

    Parameters
    ----------
    filename : str
        Path to output file
    jobs : dict(str, int)
        Mapping of job names to job IDs

    """
    colwidth = {"jobname": len("# job name"), "jobid": len("job ID")}

    colwidth = {
        "jobname": max(len(jobname) for jobname in jobs.keys()),
        "jobid": max(len(str(jobid)) for jobid in jobs.values())
        }

    colwidth["jobname"] = max(colwidth["jobname"], len("# job name"))
    colwidth["jobid"] = max(colwidth["jobid"], len("job ID"))

    row = "{{:{width[jobname]}}} {{:{width[jobid]}}}\n".format(width=colwidth)

    with open(filename, "w") as stream:
        stream.write(row.format("# job name", "job ID"))

        for jobname, jobid in jobs.items():
            stream.write(row.format(jobname, jobid))