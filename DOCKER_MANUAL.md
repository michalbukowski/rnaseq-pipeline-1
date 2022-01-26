## Simple RNA-Seq pipeline in a Docker image
The following manual was tested on Docker ver. 18.09.7, and describes how to run the DGE (differential gene expression) pipeline on Linux systems. For details see the following paper:

Bukowski M, Kosecka-Strojek M, Madry A, Zagorski-Przybylo R, Zadlo T, Gawron K, Wladyka B (2022) _Staphylococcal saoABC operon codes for a DNA-binding protein SaoC implicated in the response to nutrient deficit_. [awaiting publication]

If you find the pipeline useful, please cite the paper.

### 1. Set up the environment (optional but recommended)
Optionally, in order to allow your user to run docker without root privileges, create a group docker and add your user to it by replacing `your_user_name` with your user name. That however will itself require root privileges.
```
sudo groupadd docker
sudo usermod -aG docker your_user_name
newgrp docker
```
### 2. Download and load the Docker image
Download the image [`ubuntu-rnaseq_20.04.tar.gz`](https://mol058.mol.uj.edu.pl/suppl/rnaseq-pipeline/ubuntu-rnaseq_20.04.tar.gz) and load it to your Docker:
```
wget https://mol058.mol.uj.edu.pl/suppl/rnaseq-pipeline/ubuntu-rnaseq_20.04.tar.gz
docker load < ubuntu-rnaseq_20.04.tar.gz
```
### 3. Create a Dockerfile
In order to adjust the image file to your system environment, create a file named `Dockerfile` (plain text file) with the following content:
```
FROM ubuntu-rnaseq:20.04

ARG uid
ARG gid
ARG password

USER root
RUN addgroup --gid $gid rnaseq
RUN adduser --disabled-password --gecos '' \
            --uid $uid --gid $gid          \
            --home /home/rnaseq rnaseq
RUN usermod -aG sudo rnaseq
RUN echo "rnaseq:$password" | chpasswd
RUN chown -R rnaseq:rnaseq /home/rnaseq
USER rnaseq
```
### 4. Build your personalised image
Build a customised image `my-ubuntu-rnaseq/20.04` using the created Dockerfile and the original image `ubuntu-rnaseq/20.04` by running the following command in the directory where `Dockerfile` is located. To share your files with the container easily, it is advisable to put in the Dockerfile your system user id (`uid`), your system user group id (`gid`). To do that you need to replace `your_user_uid` and `your_user_gid` with proper numbers. By default, if you are the only user your, that will be `1000` in both cases. Use `id` command to look them up. Regarding `your_password`, feel free to come up with anything. I does not have to be you system user password, and actually for safety reasons it should not. Put your password into apostrophes to avoid any conflict between special characters used in your password and their Bash meaning. Having a password will allow you to make any modifications, by using `sudo` command, in the finally created container, should you need to do that.
```
docker build                             \
     -t         my-ubuntu-rnaseq:20.04   \
    --build-arg uid=your_user_uid        \
    --build-arg gid=your_user_gid        \
    --build-arg password='your_password' \
      ./
```
### 5. Create the _rnaseq_ container
Having your personalised image, now you can create a container from that image. The `/path/to/reads/in/your/system` must indicate the directory with RNA-Seq reads in FASTQ format (uncompressed). The reads are available at NCBI SRA database through [NCBI BioProject](https://www.ncbi.nlm.nih.gov/bioproject/) accession number [`PRJNA798259`](https://www.ncbi.nlm.nih.gov/bioproject?term=PRJNA798259%5BProject%20Accession%5D). File names must be preserved. See the list of RNA-Seq result files in the appendix. The path `/path/to/output/in/your/system` must indicate a directory where output of the pipeline will be placed.
```
docker create                                                           \
     -t                                                                 \
     -v /path/to/reads/in/your/system:/home/rnaseq/pipeline/input/reads \
     -v /path/to/output/in/your/system:/home/rnaseq/pipeline/output     \
    --workdir  /home/rnaseq/pipeline                                    \
    --hostname rnaseq                                                   \
    --name     rnaseq                                                   \
      my-ubuntu-rnaseq:20.04
```
### 6. Run the pipeline from the container
Once the container is successfully created, you can start it:
```
docker start rnaseq
```
In order to run a Bash session inside the container, run the command:
```
docker exec -it rnaseq bash
```
Inside the container your initial location will be `~/pipeline`, where the following pipeline directory structure will be created:
```
~/pipeline/
  ├── Snakefile
  ├── scripts/
  │   ├── collect.py
  │   ├── dge.r
  │   └── summary.py
  ├── input/
  │   ├── reads/
  │   │   └── (...)
  │   └── refs/
  │       └── rn.fna
  ├── output/
  └── log/
```
As you can see, you will find there Snakefile describing the pipeline. Necessary scripts will be in `scripts/`. In `input/refs/` you will have `rn.fna` multiple FASTA file with reference transcript sequences for _Staphylococcus aureus_ RN4220. In `input/reads/` you should see reads from the linked directory `/path/to/reads/in/your/system/`. You should also see `output/` which will be linked to `/path/to/output/in/your/system/`. Once the pipeline is run, `log/` directory will be automatically created. All diagnostic and error messages from tools and scripts used by the pipeline will be redirected to files in that directory. You can run the DGE pipeline on as many cores as you wish by typing the following command:
```
snakemake --cores number_of_cores
```
Once you finished the Bash session by typing exit command, in order to release system resources, you can stop the container as well:
```
docker stop rnaseq
```

### Appendix
Names of the FASTQ files with reads in [NCBI BioProject](https://www.ncbi.nlm.nih.gov/bioproject/) [`PRJNA798259`](https://www.ncbi.nlm.nih.gov/bioproject?term=PRJNA798259%5BProject%20Accession%5D) follow the pattern, which is required by the pipeline: `{strain}_{group}_{setting}_{replica}_{reads}.fastq`, e.g. `rn_wt_lg_1_R1.fastq`. Regarding strain, in the project data there are files only for `rn` (_Staphylococcus aureus_ RN4220). There are two groups: `wt` (wild type, the reference group), `mt` (mutant, _saoC_ gene mutant), sampled in two settings/conditions: `lg` (logarithmic growth phase) and `lt` (late growth phase). For each there are 3 replicas (`1` -- `3`). Reads of each are written to two files: `R1` and `R2`. All in all, there are 24 files.

Wild type in the logarithmic growth phase:
```
rn_wt_lg_1_R1.fastq
rn_wt_lg_1_R2.fastq
rn_wt_lg_2_R1.fastq
rn_wt_lg_2_R2.fastq
rn_wt_lg_3_R1.fastq
rn_wt_lg_3_R2.fastq
```
Wild type in the late growth phase:
```
rn_wt_lt_1_R1.fastq
rn_wt_lt_1_R2.fastq
rn_wt_lt_2_R1.fastq
rn_wt_lt_2_R2.fastq
rn_wt_lt_3_R1.fastq
rn_wt_lt_3_R2.fastq
```
Mutant in the logarithmic growth phase:
```
rn_mt_lg_1_R1.fastq
rn_mt_lg_1_R2.fastq
rn_mt_lg_2_R1.fastq
rn_mt_lg_2_R2.fastq
rn_mt_lg_3_R1.fastq
rn_mt_lg_3_R2.fastq
```
Mutant in the late growth phase:
```
rn_mt_lt_1_R1.fastq
rn_mt_lt_1_R2.fastq
rn_mt_lt_2_R1.fastq
rn_mt_lt_2_R2.fastq
rn_mt_lt_3_R1.fastq
rn_mt_lt_3_R2.fastq
```
