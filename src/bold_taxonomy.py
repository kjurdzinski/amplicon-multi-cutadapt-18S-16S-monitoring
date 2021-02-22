#!/usr/bin/env python

from Bio.SeqIO import parse
from urllib import request
from argparse import ArgumentParser
import pandas as pd
import sys


def get_bold_records(seq_ids):
    url_base = "http://boldsystems.org/index.php/API_Public/specimen?"
    url = "{}ids={}&format=tsv".format(url_base, "|".join(seq_ids))
    f, msg = request.urlretrieve(url)
    return f


def read_seq_file(f):
    records = []
    with open(f, 'r') as fhin:
        for record in parse(fhin, 'fasta'):
            records.append(record.id)
    return records


def get_bold_data(records, chunksize):
    chunks = [records[i:i + chunksize] for i in range(0, len(records), chunksize)]
    df = pd.DataFrame()
    for chunk in chunks:
        f = get_bold_records(chunk)
        df = pd.concat(df, pd.read_csv(f, sep="\t", index_col=0, header=0))
    return df


def main(args):
    if not args.outfile:
        out = sys.stdout
    else:
        out = args.outfile
    records = read_seq_file(args.infile)
    df = get_bold_data(records, args.num_recs)
    df.to_csv(out, sep="\t")


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
