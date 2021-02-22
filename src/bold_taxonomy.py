#!/usr/bin/env python

from Bio.SeqIO import parse
from urllib import request
from argparse import ArgumentParser
from tqdm import tqdm
import pandas as pd
import sys


def get_bold_records(seq_ids):
    """
    Uses the BOLD-API to fetch tab-separated specimen data for sequence ids
    in seq_ids

    :param seq_ids: list of sequence ids
    :return: temporary file path with tsv data
    """
    url_base = "http://boldsystems.org/index.php/API_Public/specimen?"
    url = "{}ids={}&format=tsv".format(url_base, "|".join(seq_ids))
    f, msg = request.urlretrieve(url)
    return f


def read_seq_file(f):
    """
    Reads a fasta file and stores sequence ids

    :param f: fasta file
    :return: list of sequence ids
    """
    records = []
    with open(f, 'r') as fhin:
        for record in parse(fhin, 'fasta'):
            records.append(record.id)
    return records


def get_bold_data(records, chunksize):
    """
    Iterates a list of sequence ids in chunks and fetches the corresponding
    data from BOLD using the API. Results are read into a dictionary using
    pandas.

    :param records: list of sequence record ids
    :param chunksize: number of records to pass to the API at a time
    :return: dictionary with stored data
    """
    chunks = [records[i:i + chunksize] for i in range(0, len(records), chunksize)]
    d = {}
    for chunk in tqdm(chunks,
                      desc=f"Fetching data for {len(records)} records "
                           f"({chunksize} records/chunk)",
                      total=len(chunks), ncols=100, unit=" chunk"):
        f = get_bold_records(chunk)
        df = pd.read_csv(f, sep="\t", index_col=0, header=0)
        _d = df.T.to_dict()
        d.update(_d)
    return d


def main(args):
    if not args.outfile:
        out = sys.stdout
    else:
        out = args.outfile
    records = read_seq_file(args.infile)
    d = get_bold_data(records, args.num_recs)
    df = pd.DataFrame(d)
    df.T.to_csv(out, sep="\t")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("infile", type=str,
                      help="Input sequence file")
    parser.add_argument("--num_recs", default=10, type=int,
                      help="Number of records to fetch at a time. "
                           "Defaults to 10")
    parser.add_argument("--outfile", type=str,
                        help="Output file (default: stdout)")
    args = parser.parse_args()
    main(args)
