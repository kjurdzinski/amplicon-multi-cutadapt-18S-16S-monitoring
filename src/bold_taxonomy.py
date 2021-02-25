#!/usr/bin/env python

from Bio.SeqIO import parse
from urllib import request
from argparse import ArgumentParser
from tqdm import tqdm
import pandas as pd
import sys
import os


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
        for record in tqdm(parse(fhin, 'fasta'),
                           desc=f"Reading sequence ids from {f}",
                           unit=" records"):
            records.append(record.id)
    return records



def is_file_empty(file_path):
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0


def read_existing(f, records):
    if is_file_empty(f):
        return records
    df = pd.read_csv(f, sep="\t", index_col=0, header=0)
    x = len(records)
    records = [x for x in records if not f"{x.split('|')[0]}" in df.index]
    sys.stderr.write(f"Removed {x-len(records)} already existing records\n")
    return records


def get_bold_data(records, chunksize, outfile, resume):
    """
    Iterates a list of sequence ids in chunks and fetches the corresponding
    data from BOLD using the API. Results are read into a dictionary using
    pandas.

    :param records: list of sequence record ids
    :param chunksize: number of records to pass to the API at a time
    :return: dictionary with stored data
    """
    if resume:
        records = read_existing(resume, records)
        i = 1
    else:
        i = 0

    chunks = [records[i:i + chunksize] for i in
              range(0, len(records), chunksize)]

    for chunk in tqdm(chunks, desc=f"Fetching data for {len(records)} records "
                                   f"({chunksize} records/chunk)",
                      total=len(chunks), ncols=100, unit=" chunk"):
        header = True
        if i > 0:
            header = False
        f = get_bold_records(chunk)
        df = pd.read_csv(f, sep="\t", index_col=0, header=0)
        df.index.name = "seq_id"
        df.to_csv(outfile, mode="a", sep="\t", header=header)
    return


def main(args):
    records = read_seq_file(args.infile)
    get_bold_data(records, args.num_recs, args.outfile, args.resume)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("infile", type=str, help="Input sequence file")
    parser.add_argument("outfile", type=str, help="Output file with seq info")
    parser.add_argument("--resume", type=str,
                        help="Resume from already downloaded data")
    parser.add_argument("--num_recs", default=10, type=int,
                        help="Number of records to fetch at a time. "
                             "Defaults to 10")
    args = parser.parse_args()
    main(args)
