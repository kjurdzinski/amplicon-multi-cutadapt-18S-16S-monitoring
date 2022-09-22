#!/usr/bin/env python

import re
import pandas as pd
from argparse import ArgumentParser
import sys


def compile_regex(text, ignore_case=False):
    flags = 0
    if ignore_case:
        flags = re.IGNORECASE
    return re.compile(text, flags)


def main(args):
    regex = compile_regex(args.text, args.ignore_case)
    # read sample list from workflow
    sample_df = pd.read_csv(args.sample_list, sep="\t", index_col=0)
    # read NGI delivery list
    ngi_df = pd.read_csv(
        args.ngi_list, sep="\t", index_col=0, usecols=[0, 1], names=["NGI", "USER"]
    )
    # extract samples using text search
    ngi_samples = list(ngi_df.loc[ngi_df["USER"].str.contains(regex)].index)
    sys.stderr.write(
        f"Matched {len(ngi_samples)} samples in {args.ngi_list} using {args.text}\n"
    )
    # create a regex based on matched sample strings
    sample_regex = re.compile("|".join([f"^{x}" for x in ngi_samples]))
    # slice sample list using sample_regex
    extracted_samples = sample_df.loc[
        sample_df.index.str.contains(sample_regex, regex=True)
    ]
    sys.stderr.write(
        f"Matched {extracted_samples.shape[0]} samples in sample list {args.sample_list}\n"
    )
    extracted_samples.to_csv(sys.stdout, sep="\t")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--sample_list",
        required=True,
        help="Sample list file from preprocessing " "workflow",
    )
    parser.add_argument("-n", "--ngi_list", required=True, help="NGI sample info file")
    parser.add_argument(
        "-t",
        "--text",
        required=True,
        help="Regex text to use for searching for file " "names",
    )
    parser.add_argument(
        "-i", "--ignore_case", action="store_true", help="Ignore case in regex"
    )
    args = parser.parse_args()
    main(args)
