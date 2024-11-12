# SLURM configuration profile

This is a generic SLURM configuration profile for Snakemake workflow. To use it, update the `slurm_account` and `slurm_partition` in the `config.yaml` file with your compute account and partition on your HPC cluster.

Then choose whether you want to Snakemake to use `apptainer` or `conda` to handle software dependencies by setting the `--sdm apptainer` or `--sdm conda` flag:


```bash
snakemake --sdm apptainer --profile slurm
```
or

```bash
snakemake --sdm conda --profile slurm 
```