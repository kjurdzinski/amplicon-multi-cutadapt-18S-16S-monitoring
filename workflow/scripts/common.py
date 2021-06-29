from glob import glob
import re
import os
import pandas as pd


def glob_samples(datadir):
    """
    Globs files recursively under datadir and uses regular expression to
    extract sample id. Returns a dictionary with samples.

    :param datadir: Top level data directory
    :return: dictionary with sample ids as keys and R1/R2 filepaths
    """
    sample_re = re.compile("(.+)R([12])(.*).fastq.gz")
    samples = {}
    R1_files = sorted(glob(f"{datadir}/**/*R1*.fastq.gz", recursive=True))
    R2_files = sorted(glob(f"{datadir}/**/*R2*.fastq.gz", recursive=True))
    for i, f1 in enumerate(R1_files):
        f2 = R2_files[i]
        try:
            prefix, read, suffix = sample_re.search(f1).groups()
        except AttributeError:
            print(f1)
            continue
        sample = os.path.basename(prefix).rstrip("_").lstrip("_")
        samples[sample] = {'R1': f1, 'R2': f2}
    return samples


def read_sample_list(f):
    """
    Reads samples from a tab-separated file

    :param f: sample list
    :return: dictionary of samples and R1/R2 paths
    """
    df = pd.read_csv(f, sep="\t", index_col=0)
    if "R1_type" in df.columns:
        df = df.loc[df["R1_type"]=="<class 'str'>"]
    if "R2_type" in df.columns:
        df = df.loc[df["R2_type"] == "<class 'str'>"]
    if "R1_exists" in df.columns:
        df = df.loc[df["R1_exists"]=="yes"]
    if "R2_exists" in df.columns:
        df = df.loc[df["R2_exists"] == "yes"]
    return df.to_dict(orient="index")


def shortest_primer(primers):
    """
    Returns the shortest sequence in a list

    :param primers: list of primer sequences
    :return: shortest primer
    """
    shortest = primers[0]
    for p in primers[1:]:
        if len(p)<len(shortest):
            shortest = p
    return shortest


def longest_primer(primers):
    """
    Returns the longest sequence in a list

    :param primers: list of primer sequences
    :return: longest primer
    """
    longest = primers[0]
    for p in primers[1:]:
        if len(p)>len(longest):
            longest = p
    return longest