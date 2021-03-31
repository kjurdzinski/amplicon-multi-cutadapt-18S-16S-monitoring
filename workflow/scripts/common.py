#!/usr/bin/env python

import pandas as pd
from tqdm import tqdm


def extract_species_fasta(seq_df, outdir, species):
    species_map = {}
    ranks = ["phylum", "class", "order", "family", "genus", "species"]
    i = -1
    for sp in tqdm(species, desc=f"Writing species fasta to {outdir}",
                   unit=" species"):
        i += 1
        species_map[i] = sp
        records = seq_df.loc[seq_df.species == sp]
        records = records.fillna("")
        with open(f"{outdir}/{i}.fasta", 'w') as fhout:
            for index in records.index:
                seq = records.loc[index, "seq"]
                record_id = records.loc[index, "record_id"]
                seq = seq.replace("-", "").strip("N")
                desc = ";".join([records.loc[index, x] for x in ranks])
                fhout.write(f">{record_id} {desc}\n{seq}\n")
    return species_map


def write_seqs(seq_df, outfile):
    ranks = ["phylum", "class", "order", "family", "genus", "species"]
    seq_df = seq_df.sort_values("species")
    with open(outfile, 'w') as fhout:
        for index in tqdm(seq_df.index, desc=f"Writing sequences to {outfile}",
                          unit=" seqs"):
            seq = seq_df.loc[index, "seq"]
            record_id = records.loc[index, "record_id"]
            seq = seq.replace("-", "").strip("N")
            if "N" in seq:
                continue
            desc = ";".join([records.loc[index, x] for x in ranks])
            fhout.write(f">{record_id} {desc}\n{seq}\n")


def filter_bold(sm):
    genes = sm.params.genes
    phyla = sm.params.phyla
    # Read info
    df = pd.read_csv(sm.input[0], sep="\t", usecols=[0, 4, 7, 8, 9, 10, 11, 12],
                     names=["record_id", "bold_id", "phylum", "class", "order",
                            "family", "genus", "species"])
    # Filter dataframe to phyla
    df = df.loc[df.phylum.isin(phyla)]
    # Read fasta
    seqs = pd.read_csv(sm.input[1], header=None, sep="\t", index_col=0,
                       names=["record_id", "gene", "seq"])
    # Filter fasta to gene(s)
    seqs = seqs.loc[seqs.gene.isin(genes)]
    # Merge in order to get the intersection
    seq_df = pd.merge(df, seqs, left_on="record_id", right_index=True,
                      how="inner")
    # Write to file
    seq_df.drop(["seq"], axis=1).head().to_csv(sm.output.info, header=True,
                                               index=False, sep="\t")
    # Write seqs to file
    write_seqs(seq_df, sm.output.fasta)

    # # Extract species fasta  # species = seq_df.species.unique()  # species_map = extract_species_fasta(seq_df, sm.output.sp_dir, species)  # species_map_df = pd.DataFrame(species_map, index=[0]).T  # species_map_df.index.name = "species_id"  # species_map_df.columns = ["species"]  # species_map_df.to_csv(sm.output.sp_map)


def main(sm):
    toolbox = {'filter_bold': filter_bold}
    toolbox[sm.rule](sm)


if __name__ == '__main__':
    main(snakemake)
