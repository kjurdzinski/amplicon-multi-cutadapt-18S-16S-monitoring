#!/bin/bash -l
 
#SBATCH -A naiss2023-5-110
#SBATCH -p core
#SBATCH -n 1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=krzysztof.jurdzins@scilifelab.se
#SBATCH -t 00:40:00
#SBATCH -J creating_cutadapt_env

conda remove amp-multi-cut

cd /crex/proj/snic2020-6-126/projects/plankton_monitoring/seq_2015_2017_analysis/amplicon-multi-cutadapt/
conda env create -f environment.yml
