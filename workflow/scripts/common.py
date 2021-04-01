#!/usr/bin/env python

import pandas as pd
from tqdm import tqdm
import sys
import shutil
import os

def write_seqs(seq_df, outfile, tmpfile):
    ranks = ["phylum", "class", "order", "family", "genus", "species"]
    # Sort sequences by species
    seq_df = seq_df.sort_values("species")
    tmpfile = os.path.expandvars(tmpfile)
    outfile = os.path.abspath(outfile)
    with open(tmpfile, 'w') as fhout:
        for index in tqdm(seq_df.index, desc=f"Writing sequences to {tmpfile}",
                          unit=" seqs"):
            seq = seq_df.loc[index, "seq"]
            record_id = seq_df.loc[index, "record_id"]
            seq = seq.replace("-", "").strip("N")
            if "N" in seq:
                continue
            desc = ";".join([seq_df.loc[index, x] for x in ranks])
            fhout.write(f">{record_id} {desc}\n{seq}\n")
    sys.stderr.write(f"Moving {tmpfile} to {outfile}\n")
    shutil.move(tmpfile, outfile)


def filter_bold(sm):
    genes = sm.params.genes
    phyla = sm.params.phyla
    # Read info
    sys.stderr.write(f"Reading info file {sm.input[0]}\n")
    df = pd.read_csv(sm.input[0], sep="\t", usecols=[0, 4, 7, 8, 9, 10, 11, 12],
                     names=["record_id", "bold_id", "phylum", "class", "order",
                            "family", "genus", "species"],
                     dtype={'bold_id': str})
    df.fillna("", inplace=True)
    sys.stderr.write(f"{df.shape[0]} records read\n")
    # Filter dataframe to phyla
    sys.stderr.write("Filtering info file\n")
    df = df.loc[df.phylum.isin(phyla)]
    sys.stderr.write(f"{df.shape[0]} records remaining\n")
    # Read fasta
    sys.stderr.write(f"Reading fasta file {sm.input[1]}\n")
    seqs = pd.read_csv(sm.input[1], header=None, sep="\t", index_col=0,
                       names=["record_id", "gene", "seq"])
    sys.stderr.write(f"{seqs.shape[0]} sequences read\n")
    # Filter fasta to gene(s)
    sys.stderr.write(f"Filtering sequences to gene(s) of interest\n")
    seqs = seqs.loc[seqs.gene.isin(genes)]
    sys.stderr.write(f"{seqs.shape[0]} sequences remaining\n")
    # Merge in order to get the intersection
    sys.stderr.write(f"Merging info and sequences\n")
    seq_df = pd.merge(df, seqs, left_on="record_id", right_index=True,
                      how="inner")
    sys.stderr.write(f"{seq_df.shape[0]} sequence records remaining\n")
    # Write to file
    seq_df.drop(["seq"], axis=1).to_csv(sm.output.info, header=True,
                                               index=False, sep="\t")
    # Write seqs to file
    write_seqs(seq_df, sm.output.fasta, sm.params.tmpf)


def main(sm):
    toolbox = {'filter_bold': filter_bold}
    toolbox[sm.rule](sm)


if __name__ == '__main__':
    main(snakemake)
