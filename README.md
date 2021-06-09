# Insect biome atlas
Private github repository for the Insect Biome Atlas project.

This repository hosts a snakemake workflow for trimming and QC
of paired-end fastq files. The trimming is done in three steps
using `cutadapt`.

## Setup

### Software requirements
Install required packages with conda and activate environment:

```bash
conda env create -f environment.yml
conda activate insect-biome
```

### Input data

The workflow finds all fastq-files under a top-level directory defined in the 
workflow config:

```yaml
paths:
  raw_data_dir: data
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
paths:
  raw_data_dir: /proj/delivery/P00001
```

then run the workflow with `--configfile <path-to-your-config>.yaml`

## Running the workflow

The basic command for running the workflow is:

```bash
snakemake -j 4 --use-conda --conda-frontend mamba
```

This runs snakemake with 4 cores and makes sure that workflow dependencies
are handled using the 

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

