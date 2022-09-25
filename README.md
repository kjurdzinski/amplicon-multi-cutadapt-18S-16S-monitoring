# Amplicon-multi-cutadapt

This repository hosts a snakemake workflow for trimming and QC
of paired-end fastq files. The trimming is done in four steps
using `cutadapt`.

## Installation

Use conda to create and activate the software environment required to start the 
workflow:

```bash
conda env create -f environment.yml
conda activate amp-multi-cut
```

**Note**: If you don't have conda installed, please visit the [conda docs](https://docs.conda.io/en/latest/miniconda.html)
for instructions and installation links.

## Running the workflow

This workflow is meant to be downloaded from its Github repository, either by 
cloning or downloading a release tarball from the [release page](https://github.com/biodiversitydata-se/amplicon-multi-cutadapt/releases).

After you've downloaded the workflow (and installed the software environment, see above)
you run the workflow from the root of the amplicon-multi-cutadapt directory
(where this `README.md` file is located). Since this is a Snakemake workflow
you need to run the `snakemake` command from the terminal to start it. 

To try it out in practice you can run the following:

```bash
snakemake --profile test
```

This will run the workflow on a small test dataset (the actual data is under 
`test/data/`). 

**Note**: After the workflow completes, trimmed and processed fastq files 
can be found under the `results/cutadapt/` directory. 

The way that the `--profile` flag works is that it allows you to 
specify a folder containing configuration parameters for snakemake. In this case
it points to the `test/` subdirectory where the file `config.yaml` specifies the 
command line options to use with snakemake.

In addition to the `test` profile, the workflow comes with pre-configured 
profiles for: 
1) running locally on your own computer
2) running on HPC clusters with the SLURM workload manager (_e.g._ the UPPMAX cluster)
 

To use them you specify `--profile local` and `--profile slurm` respectively. So
if you're running on your local computer simply do:

```bash
snakemake --profile local
```

and if you're running remotely on a SLURM cluster do:

```bash
snakemake --profile slurm
```

### Configuration files

There are a few more configuration parameters you can set that will influence 
how the workflow runs. The default values are specified in the file `config/config.yaml`:

```yaml
# DEFAULT CONFIG PARAMS IN config/config.yaml
cutadapt:
    threads: 16
    expected_read_length: 251
primers:
    forward:
        - "CCHGAYATRGCHTTYCCHCG"
        - "ACCHGAYATRGCHTTYCCHCG"
        - "GACCHGAYATRGCHTTYCCHCG"
        - "TGACCHGAYATRGCHTTYCCHCG"
    reverse:
        - "CDGGRTGNCCRAARAAYCA"
        - "TCDGGRTGNCCRAARAAYCA"
        - "ATCDGGRTGNCCRAARAAYCA"
        - "GATCDGGRTGNCCRAARAAYCA"
data_dir: "data"
sample_list: ""
```

As you can see, these parameters define _e.g._ the primers to use and the 
expected read length for your data. If you need to change these settings you can
either update the `config/config.yaml` file directly, or make a new one and set
your parameters there. Then you need to point snakemake to the new config file 
with `--configfile <path-to-your-config-file>.yaml` on the command line.

### Getting your data into the workflow

The workflow searches for fastq files under a directory specified by 
the `data_dir:` config parameter. By default, this parameter is set to `data/`.
One easy way to integrate your own data is to symlink a data delivery folder inside
`data/`. For instance say you have data delivered to a directory
`/proj/delivery/P00001/`, then you can either symlink that folder into `data/`:

```bash
ln -s /proj/delivery/P00001 data/
```

or you can make a config file (in `yaml` format) that contains:

```yaml
data_dir: /proj/delivery/P00001
```

then run the workflow with `--configfile <path-to-your-config-file>.yaml`

### Sample list (when you have a lot of samples)

If you have **a lot** of samples it can take a long time for the workflow to
locate each R1/R2 input file. This can slow down even so called dry-runs of the 
workflow and make it difficult to work with. In that case you may want to create
a sample list that specifies each sample and the respective R1/R2 file paths so
that the workflow doesn't have to do this search on every instance.

To generate such a sample list first make sure you've set the `data_dir` 
parameter correctly so that it points to a directory containing your data, then
run snakemake with `samples/sample_list.tsv` added to the command. 

Let's try that in practice for the test dataset:

```bash
snakemake --config data_dir=test/data --profile test samples/sample_list.tsv
```

Here we specify `data_dir=test/data` on the command line instead of in a config 
file. This is generally not recommended because config files make it easier to
track what parameters have been used, but for this example it's ok.

The workflow will now locate all the R1/R2 fastq-files under your configured 
`data_dir` path and create a tab-delimited file called `sample_list.tsv` under
the directory `samples/`. Using the `samples/` directory is required at this step,
as is the `.tsv` suffix, but otherwise you can name the file anything you like, 
so _e.g._ `snakemake --profile test samples/my-sample-list.tsv` will also work.

Note that if you're using a separate configuration file you have to update the 
snakemake call above to include `--configfile <path-to-your-configfile>`.

You only have to generate this sample list once, and then you can make the 
workflow use the sample list by updating your configuration file with:

```yaml
sample_list: samples/sample_list.tsv
```

## QC of reads

If you want to get a QC report for the processed fastq files you can add the 
file pattern `results/multiqc_4.html` to the snakemake call, _e.g._:

```bash
snakemake --profile test results/multiqc_4.html
```

This will output a MultiQC report at `results/multiqc_4.html`. Here the `_4` part
means that this is a report for fastq files produced from the 4th cutadapt step
(see bottom of this README for explanation of the different steps). You may also
ask for a qc report from either of the other steps (1-3), but be aware that if 
you've already run the workflow to completion this will force the workflow to 
rerun the intermediate steps since intermediate fastq files are removed when the
workflow finishes.

## Extracting a subset of samples
In case you have a data directory with a lot fastq files, and you've generated
a sample list as described above (by letting the workflow search the contents 
of a data directory) but you want to run the workflow on only a subset of those 
samples there's a utility script at `workflow/scripts/extract_samples.py`. This
script allows you to input:

1. the full sample list
2. a file with sample names as given by the sequencer (first column) 
together with user defined sample names (second column) and
3. a search string

and will then output lines from the full sample list that match with the 
specified text string. 

For example:

Say you have a data directory `/data/sequencing1/` with the following data:
```
└── sequencing1
    ├── sample0001
    │   ├── sample0001_R1.fastq.gz
    │   └── sample0001_R2.fastq.gz
    ├── sample0002
    │   ├── sample0002_R1.fastq.gz
    │   └── sample0002_R2.fastq.gz
    ...
    └── sample0010
        ├── sample0010_R1.fastq.gz
        └── sample0010_R2.fastq.gz
```

Running the workflow with:

```bash
snakemake --config data_dir=data/sequencing1 -j 1 samples/sequencing1.tsv
```

would then generate a sample list `samples/sequencing1.tsv` like this:

| sample     | R1                                                  | R1_type       | R1_exists | R2                                                 | R2_type       | R2_exists |
|------------|-----------------------------------------------------|---------------|-----------|----------------------------------------------------|---------------|-----------|
| sample0001 | data/sequencing1/sample0001/sample0001_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0001/sample0001_R2.fastq.gz | <class 'str'> | yes       |
| sample0002 | data/sequencing1/sample0002/sample0002_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0002/sample0002_R2.fastq.gz | <class 'str'> | yes       |
| sample0003 | data/sequencing1/sample0003/sample0003_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0003/sample0003_R2.fastq.gz | <class 'str'> | yes       |
...

Now, say that you also have a file `sequencing1_sample_info.txt` with the 
following contents:

```
SEQUENCING_ID    USER ID
sample0001       SOIL_MAR_1
sample0002       SOIL_JUN_1
sample0003       WATER_MAR_1
sample0004       WATER_JUN_1
sample0005       SOIL_MAR_2
sample0006       SOIL_JUN_2
sample0007       WATER_MAR_1
sample0008       WATER_JUN_2
sample0009       seq1_neg_control1
sample0010       seq1_neg_control2
```

Note that this file can have more columns, but sample names in the first column 
have to be included in the beginning of the sample names as given in the first 
column of the full sample list (`samples/sequencing1.tsv` in this example).

Now to extract only samples matching `_MAR_` in the `USER ID` column of `sequencing1_sample_info.txt` 
we can run:

```bash
python workflow/scripts/extract_samples.py -s samples/sequencing1.tsv -i sequencing1_sample_info.txt -t "_MAR_"
```

which would output:
```
sample  R1      R1_type R1_exists       R2      R2_type R2_exists
sample0001      data/sequencing1/sample0001/sample0001_R1.fastq.gz      <class 'str'>   yes     data/sequencing1/sample0001/sample0001_R2.fastq.gz      <class 'str'>   yes
sample0003      data/sequencing1/sample0003/sample0003_R1.fastq.gz      <class 'str'>   yes     data/sequencing1/sample0003/sample0003_R2.fastq.gz      <class 'str'>   yes
sample0005      data/sequencing1/sample0005/sample0005_R1.fastq.gz      <class 'str'>   yes     data/sequencing1/sample0005/sample0005_R2.fastq.gz      <class 'str'>   yes
sample0007      data/sequencing1/sample0007/sample0007_R1.fastq.gz      <class 'str'>   yes     data/sequencing1/sample0007/sample0007_R2.fastq.gz      <class 'str'>   yes
sample0008      data/sequencing1/sample0008/sample0008_R1.fastq.gz      <class 'str'>   yes     data/sequencing1/sample0008/sample0008_R2.fastq.gz      <class 'str'>   yes
```

The text string you give with `-t` can be a regular expression, for example
if we want to output all samples except the two negative controls
(`seq1_neg_control1`, `seq1_neg_control2`) we could run:

```
python workflow/scripts/extract_samples.py -s samples/sequencing1.tsv -i sequencing1_sample_info.txt -t "_\d$"
```

where `-t "_\d$"` matches all samples ending in an underscore and a digit.

## Explanation of the cutadapt steps

The workflow processes fastq files in four consecutive `cutadapt` steps:

1. Discard all reads with the Illumina TruSeq adapters in either the 5' or 3'  
   end of sequences. 
2. Search for and trim primer sequences from the start of reads in R1 and R2
   files using forward and reverse primers, respectively. Remove any untrimmed 
   read. This step is done with additional settings `--no-indels` and `-e 0` in 
   order to only accept perfect matches.
3. Discard any remaining reads that still contain primer sequences.
4. Trim reads to a fixed length. This length is calculated by subtracting the 
   length of the longest primer from the read length defined by the `expected_read_length:`
   parameter under the `cutadapt:` section in the config file (default value is 251).