# Amplicon-multi-cutadapt

This repository hosts a snakemake workflow for trimming and QC
of paired-end fastq files. The trimming is done in four steps
using `cutadapt`.

- [Installation](#installation)
  - [Using pixi](#using-pixi-recommended)
  - [Using conda](#using-conda)
- [Running the workflow](#running-the-workflow)
- [Configuration](#configuration)
- [Getting your data into the workflow](#getting-your-data-into-the-workflow)
  - [Using the `data` directory](#using-the-data-directory)
  - [Using a sample list](#using-a-sample-list)
- [QC of reads](#qc-of-reads)
- [Extracting a subset of samples](#extracting-a-subset-of-samples)
- [Explanation of the cutadapt steps](#explanation-of-the-cutadapt-steps)

## Installation

First clone the repository to a location on your system:
    
```bash
git clone git@github.com:insect-biome-atlas/amplicon-multi-cutadapt.git
```

Then `cd` into the repository:

```bash
cd amplicon-multi-cutadapt
```

The software required to run this workflow can be installed with either [pixi](https://pixi.sh/latest) or [conda](https://docs.conda.io/en/latest/miniconda.html).

### Using pixi (recommended)

If you have not installed pixi yet, you can do so by running the following command:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

After installation, restart your terminal and run `pixi --version` to verify that the installation was successful.

> [!TIP] 
> If the `pixi --version` command does not work, you may need to manually
> add the path to the pixi binary to your `PATH` environment variable. Open the
> file `~/.bashrc` (or `~/.zshrc` if using zsh) in a text editor and add the
> following line to the end of the file:
> ```bash
> export PATH="$PATH:$HOME/.pixi/bin"
> ```
> Save the file and run `source ~/.bashrc` (or `source ~/.zshrc` if using zsh) to
> apply the changes.

After installing pixi, you can create and activate the software environment
required to start the workflow by running the following command from the root of
the repository:

```bash
pixi shell
```

You should see `(amplicon-multi-cutadapt)` prepended to your terminal prompt,
which indicates that the software environment has been activated.

### Using conda

To use conda to install the software environment, you need to have conda
installed. Follow the instructions for your operating system
[here](https://docs.anaconda.com/miniconda/#quick-command-line-install).

Next, you can create and activate the software environment by running the
following commands from the root of the repository:

```bash
conda env create -f environment.yml
conda activate amp-multi-cut
```

## Running the workflow

After you've downloaded the workflow and installed the software environment
you run the workflow from the root of the amplicon-multi-cutadapt directory
(where this `README.md` file is located). 

> [!TIP] 
> If you are running this workflow on a cluster with the SLURM workload
> manager, see additional tips in the [slurm/README.md](slurm/README.md) file.
> If you are running on the Dardel HPC cluster, see specific instruction in
> the [dardel/README.md](dardel/README.md) file.

Software dependencies are managed by snakemake either using `conda` or
`apptainer` and you select which one to use by specifying `--sdm apptainer` or 
`--sdm conda` on the command line.

To run the workflow on a small test dataset you can do:

```bash
snakemake --sdm apptainer --profile test 
```

or

```bash
snakemake --sdm conda --profile test 
```

Follow the instructions on how to [configure](#configuration) and [get your data
into the workflow](#getting-your-data-into-the-workflow) below, then either run the 
workflow on your local computer using:

```bash
snakemake --profile local --sdm apptainer # or --sdm conda
```

or follow the instructions in the [dardel/README.md](dardel/README.md) or
[slurm/README.md](slurm/README.md) files to run the workflow on a cluster.

## Configuration

You can configure the workflow by editing the `config/config.yaml` file. This
file contains the following default settings:

```yaml
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
multiqc_steps: [4]
ampliseq_sample_sheet: "results/ampliseq_sample_sheet.tsv"
```

The `expected_read_length` defines the expected read length after trimming. In
the final cutadapt step, `R1` and `R2` reads are trimmed to a fixed length
calculated by subtracting the length of the longest forward or reverse primer,
respectively, from this value.

The `primers` section contains lists of forward and reverse primers used to
sequence your data.

The `data_dir` parameter specifies the directory where the workflow will look
for fastq files matching the file pattern `*R1*.fastq.gz` and `*R2*.fastq.gz` in
any subdirectory.

Alternatively, you can set the `sample_list` parameter to point to a
tab-separated file containing a list of samples and their respective R1/R2 file
paths. This file should have the following format:

| sample | R1 | R2 |
|--------|----|----|
| sample1 | /path/to/sample1_R1.fastq.gz | /path/to/sample1_R2.fastq.gz |
| sample2 | /path/to/sample2_R1.fastq.gz | /path/to/sample2_R2.fastq.gz |

The `multiqc_steps` parameter specifies for which cutadapt step(s) to generate
a MultiQC report. The default value `[4]` generates a report for the final
cutadapt step only. To generate a report for each step, set this parameter to
`[1, 2, 3, 4]` or leave it empty `[]` to disable MultiQC reports.

The `ampliseq_sample_sheet` parameter specifies the path a file that will be created by the workflow containing the sample names and the corresponding primer sequences used for trimming. This file can be used as input for the [AmpliSeq](https://nf-co.re/ampliseq) workflow.

## Getting your data into the workflow

### Using the `data` directory

One easy way to integrate your own data is to symlink a data delivery folder
inside `data/` (the default for `data_dir`). For instance say you have data
delivered to a directory `/proj/delivery/P00001/`, then you can either symlink
that folder into `data/`:

```bash
ln -s /proj/delivery/P00001 data/
```

or you can edit `data_dir` in [config/config.yaml](config/config.yaml) to:

```yaml
data_dir: /proj/delivery/P00001
```

### Using a sample list

If you have **a lot** of samples it can take a long time for the workflow to
locate each R1/R2 input file. This can slow down even so called dry-runs of the 
workflow and make it difficult to work with. In that case you may want to create
a sample list that specifies each sample and the respective R1/R2 file paths so
that the workflow doesn't have to do this search on every instance.

To generate such a sample list first we can set the `data_dir` parameter on the
fly and generate a sample list with snakemake. If you have data in
`/proj/delivery/P00001` and you want to generate a sample list called
`samples/P00001.tsv` you can do:

```bash
snakemake --config data_dir=/proj/delivery/P00001 --profile local samples/P00001.tsv
```

The workflow will locate all the R1/R2 fastq-files under your configured
`/proj/delivery/P00001` and create a tab-delimited file called
`samples/P00001.tsv`. Using the `samples/` directory is required at this step,
as is the `.tsv` suffix, but otherwise you can name the file anything you like,
so _e.g._ `samples/my-sample-list.tsv` will also work whereas
`samples/my-sample-list.txt` or `my-sample-list.tsv` will not.

You only have to generate this sample list once, and then you can make the
workflow use the sample list by updating the `sample_list` config parameter in
[config/config.yaml](config/config.yaml). Using the example above it would be:

```yaml
sample_list: samples/P00001.tsv
```

The sample list generated using this method will contain the additional columns
`R1_type`, `R1_exists`, `R2_type`, and `R2_exists` which are used by the
workflow to check if the files are valid. The `R1_type` and `R2_type` columns
should only contain `<class 'str'>` and the `R1_exists` and `R2_exists` columns
should contain `yes`. If the files are not found or not readable the `R1_exists`
and `R2_exists` columns will contain `no`.

## QC of reads

The workflow generates a MultiQC report `results/multiqc_4.html` for the final
cutadapt step by default. You may also configure the `multiqc_steps` config
parameter to get a qc report from either of the other steps (1-3).

> [!IMPORTANT] 
> Be aware that if you've already run the workflow to completion and you then
> update the `multiqc_steps` parameter with additional steps this will force the
> workflow to rerun the intermediate steps since intermediate fastq files are
> removed when the workflow finishes.

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
snakemake --config data_dir=data/sequencing1 --profile local samples/sequencing1.tsv
```

would then generate a sample list `samples/sequencing1.tsv` like this:

| sample     | R1                                                  | R1_type       | R1_exists | R2                                                 | R2_type       | R2_exists |
|------------|-----------------------------------------------------|---------------|-----------|----------------------------------------------------|---------------|-----------|
| sample0001 | data/sequencing1/sample0001/sample0001_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0001/sample0001_R2.fastq.gz | <class 'str'> | yes       |
| sample0002 | data/sequencing1/sample0002/sample0002_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0002/sample0002_R2.fastq.gz | <class 'str'> | yes       |
| sample0003 | data/sequencing1/sample0003/sample0003_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0003/sample0003_R2.fastq.gz | <class 'str'> | yes       |
| ...       | ...                                                 | ...           | ...       | ...                                                | ...           | ...       |
| sample0010 | data/sequencing1/sample0010/sample0010_R1.fastq.gz  | <class 'str'> | yes       | data/sequencing1/sample0010/sample0010_R2.fastq.gz | <class 'str'> | yes       |

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

```bash
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