# Configuration profile for the Dardel HPC cluster

This repository contains a Snakemake configuration profile for the Dardel HPC
cluster. Follow the instructions below to set up the profile and configure
Snakemake to use your personal temporary storage under `$PDC_TMP` so that you
won't run into storage issues.

## Set your compute account

To use this profile, update `slurm_account` in the `config.yaml` file with your compute account on Dardel.

For example, if your compute account is `naiss2024-1-100`, update the `config.yaml` file as follows:

```yaml
default-resources:
  slurm_account: "naiss2024-1-100"
  slurm_partition: shared
  cpus_per_task: 1
  runtime: 120
  tasks: f"{threads}"
  mem_mb: 888
```

## Choose the software deployment method

You can either use `apptainer` or `conda` to handle software dependencies. The recommended method is `apptainer` which requires that you also load the PDC and apptainer modules. So first run:

```bash
module load PDC apptainer
```
Then you can run the workflow with the following command:

```bash
snakemake --sdm apptainer --profile dardel
```

If you instead want to use `conda`, you can run the workflow with the following command:

```bash
snakemake --sdm conda --profile dardel
```

## Using your personal temporary storage

Both Snakemake, Apptainer and Conda will occasionally need to download or write temporary files to disk. These files can take up quite a lot space so in order to avoid storage issues you want these files to be written to your personal temporary storage under `$PDC_TMP`.

To do this, edit your `$HOME/.bashrc` file (`$HOME/.zshrc` if you are using zsh) and add the following lines:

```bash
export TMPDIR=$PDC_TMP
export APPTAINER_CACHEDIR="$PDC_TMP/.cache/apptainer"
export SNAKEMAKE_OUTPUT_CACHE="$PDC_TMP/.cache/snakemake"
```

Then source the `$HOME/.bashrc` file (`$HOME/.zshrc` if you are using zsh) to apply the changes:

```bash
source $HOME/.bashrc # or source $HOME/.zshrc if you are using zsh
```

Then create the directories:

```bash
mkdir -p $APPAINER_CACHEDIR $SNAKEMAKE_OUTPUT_CACHE
```

Next, set up conda to use your personal temporary storage for package downloads. Edit the file `$HOME/.condarc` so that it contains:

```yaml
pkgs_dirs:
  - $PDC_TMP/.cache/pkgs
```

and create the directory:

```bash
mkdir -p $PDC_TMP/.cache/pkgs
```

