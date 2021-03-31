#!/usr/bin/env python


def extract_bold_taxa(sm):
    with open(sm.input[0], 'r') as fhin, open(sm.output[0], 'w') as fhout:
        for line in fhin:
            items = line.rstrip().split("\t")
            indices = [0, 7, 8, 9, 10, 11, 12]
            record_id, p, c, o, f, g, s = [items[i] for i in indices]
            if p == sm.wildcards.taxa:
                fhout.write(f"{record_id}\n")


def extract_bold_seqs(sm):
    with open(sm.input[0], 'r') as fhin, open(sm.output[0], 'w') as fhout:
        for line in fhin:
            try:
                record_id, gene, seq = line.rstrip().rsplit()
            except ValueError:
                continue
            if gene == sm.wildcards.gene:
                fhout.write(f">{record_id} {gene}\n{seq}\n")


def main(sm):
    toolbox = {'extract_bold_taxa': extract_bold_taxa,
               'extract_bold_seqs': extract_bold_seqs}
    toolbox[sm.rule](sm)


if __name__ == '__main__':
    main(snakemake)
