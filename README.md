# Insect biome atlas
Private github repository for the Insect Biome Atlas project.

This repository hosts a snakemake workflow for trimming and QC
of paired-end fastq files. The trimming is done in four steps
using `cutadapt`.

## Setup

### Software requirements
Install required packages with conda and activate environment:

```bash
conda env create -f environment.yml
conda activate insect-biome
```

### Data directory

The workflow finds all fastq-files under a top-level directory defined in the 
workflow config:

```yaml
data_dir: data
```

By default the workflow searches for fastq files under `data/`.
One easy way to integrate your data is to symlink a data delivery folder inside
`data/`. For instance say you have data delivered to a directory
`/proj/delivery/P00001/`, then you can either symlink that folder into `data/`:

```bash
ln -s /proj/delivery/P00001 data/
```

or you can make a config file that contains:

```yaml
data_dir: /proj/delivery/P00001
```

then run the workflow with `--configfile <path-to-your-config>.yaml`

### Sample list (when you have a lot of samples)

If you have **a lot** of samples it can take a long time for the workflow to
locate each R1/R2 input file. This can slow down even so called dry-runs of the 
workflow and make it difficult to work with. In that case you may want to create
a sample list that specifies each sample and the respective R1/R2 file paths so
that the workflow doesn't have to do this search on every instance.

To generate such a sample list first make sure you've set the `data_dir` 
parameter correctly in your configuration file then run:

```bash
snakemake -j 1 samples/sample_list.tsv
```

The workflow will now locate all the R1/R2 fastq-files under your configured 
`data_dir` path and create a tab-delimited file called `sample_list.tsv` under
the directory `samples/`. Using the `samples/` directory is required at this step,
as is the `.tsv` suffix, but otherwise you can name the file anything you like, 
so _e.g._ `snakemake -j 1 samples/my-sample-list.tsv` will also work.

Note that if you're using a separate configuration file you have to update the 
snakemake call above to include `--configfile <path-to-your-configfile>`.

You only have to generate this sample list once, and then you can make the 
workflow use the sample list by updating your configuration file with:

```yaml
sample_list: samples/sample_list.tsv
```

## Running the workflow

The basic command for running the workflow is:

```bash
snakemake -j 4 --use-conda --conda-frontend mamba
```

This runs snakemake with 4 cores and makes sure that workflow dependencies
are handled using the `mamba` package manager. If `mamba` is not installed on
your system you can do so by running `conda install -c conda-forge mamba`.

## Test data

This repo comes with a few test fastq files located in subdirectories under 
`tests/data/`. To try the workflow out with these files you must first zip them,
_e.g._ by running:

```bash
gzip tests/data/*/*.fastq
```

Then you can do a test run on this data by running:

```
snakemake --config data_dir=tests/data -j 4 --use-conda --conda-frontend mamba
```

## Background
The Insect Biome Atlas (IBA) is an international collaborative effort to 
describe in detail the insect faunas of two biologically and geologically very 
different countries: Sweden and Madagascar. The project, one of the largest 
ongoing insect biodiversity surveys, addresses key questions about the insect 
diversity: How are insect species distributed across habitats, sites and 
seasons? What are the key environmental factors shaping insect diversity?

Collection phase lasted a whole year (2019) in each country and was done by 
means of Malaise traps: 200 in Sweden and 50 in Madagascar. Summing up, the IBA 
collected more than 8000 insect community samples. Several other types of 
samples and ecological measurements were also collected at the trap sites to 
gather a full understanding of the ecological roles of the organisms that 
comprise the insect biome in these countries. Analysis of the samples include 
identification of all insects and the organisms they interact with, such as 
pathogens as well as symbiotic fungi and bacteria - this is achieved by using 
novel DNA techniques. The results and material collected during the IBA project 
will be useful for scientists interested in systematics, taxonomy and insect 
ecology and evolution for many years to come.

In Sweden the Malaise traps were managed by over 100 volunteers, which makes 
this project one of the largest citizen science projects to take place in 
Scandinavia.

IBA consortium brings together researchers from many countries and institutes 
including Natural History Museum in Stockholm, Stockholm University, Swedish 
University of Agricultural Sciences, Uppsala, SciLifeLab, KTH Royal Institute 
of Technology Stockholm, Madagascar Biodiversity Center, Jagiellonian 
University, Krakow, Poland. 

