from glob import glob
import re
import os

def read_samples(datadir):
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