## Simple RNA-Seq pipeline
Differential gene expression pipeline utilising Salmon and Bioconductor DESeq2 for Illumina RNA-Seq squencing results for reversed stranded libraries. For detail see the following paper:

Bukowski M, Kosecka-Strojek M, Madry A, Zagorski-Przybylo R, Zadlo T, Gawron K, Wladyka B (2022) _Staphylococcal saoABC operon codes for a DNA-binding protein SaoC implicated in the response to nutrient deficit_. [awaiting publication]

If you find the pipeline useful, please cite the paper.

### 1. Environment
The pipeline was created and tested in the following set-up:
- Miniconda3 environment:
  - Python (3.8.5)
  - Snakemake (5.32.0)
  - Salmon (1.4.0)
  - Pandas (1.1.4)
- R (4.0.3):
  - Bioconductor DESeq2 (1.30.0)
  - Bioconductor tximport ()
  - optparse ()

### 2. Directory structure and pipeline files
Names of the FASTQ files with reads in [NCBI BioProject](https://www.ncbi.nlm.nih.gov/bioproject/) [`PRJNA798259`](https://www.ncbi.nlm.nih.gov/bioproject?term=PRJNA798259%5BProject%20Accession%5D) follow the pattern, which is required by the pipeline: `{strain}_{group}_{setting}_{replica}_{reads}.fastq`, e.g. `rn_wt_lg_1_R1.fastq`. Regarging strain, in the project data there are files only for `rn` (_Staphylococcus aureus_ RN4220). There are two groups: `wt` (wild type, the reference group), `mt` (mutant, _saoC_ gene mutant), sampled in two settings/conditions: `lg` (logarithmic growth phase) and `lt` (late growth phase). For each there are 3 replicas (`1` -- `3`). Reads of each are written to two files: `R1` and `R2`. All in all, there are 24 files.

The pipeline utilises the following directory structure:
```
your_pipeline_location/
|--- Snakefile
|--- scripts/
|    |--- collect.py
|    |--- dge.r
|    |--- summary.py
|--- input/
|    |--- reads/
|    |    |--- (...)
|    |--- refs/
|         |--- rn.fna
|--- output/
|--- log/
```
In the working directory you can find the Snakefile describing the pipeline. Necessary scripts are in `scripts/`. In `input/refs/` you will have `rn.fna` multiple FASTA file with reference transcript sequences for Staphylococcus aureus RN4220. In `input/reads/` you should place reads from [NCBI BioProject](https://www.ncbi.nlm.nih.gov/bioproject/) [`PRJNA798259`](https://www.ncbi.nlm.nih.gov/bioproject?term=PRJNA798259%5BProject%20Accession%5D). Directories `output/` and `log/` will be created automatically once the pipeline is run. All diagnostic and error messages from tools and scripts used by the pipeline will be redirected to files in the `log/` directory.

### 3. Pipeline architecture
The pipline described in the Snakefile encompasses the following stages:
1. **index** -- preparation of an index of reference transcript sequences with Salmon.
1. **quant** -- read mapping and counts with Salmon.
1. **collect** -- preparation of metadata for Salmon quant files with `scripts/collect.py`.
1. **dge** -- differential gene expression with `scripts/dge.r` usitlising DESeq2 library.
1. **summary** -- generation of the final output in TSV format with `scripts/summary.py`.

More detailed description on how the pipeline works you will find in comments both in the Snakefile and the script files.

### 4. Running the pipeline
Providing that you have the environment properly set up, you can run the pipeline from the directory with `Snakefile` on as many cores as you wish:
```
snakemake --cores number_of_cores
```
