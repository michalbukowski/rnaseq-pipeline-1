# Created by Michal Bukowski (michal.bukowski@tuta.io) under GPL-3.0 license

# Differential gene expression pipeline utilising Salmon and Bioconductor DESeq2
# for Illumina RNA-Seq squencing results for reversed stranded libraries.

# If you find it useful, please cite:
# Bukowski M et al. (2022) Staphylococcal saoABC operon codes for
# a DNA-binding protein SaoC implicated in the response to nutrient deficit.
# [awaiting publication]

# FASTQ files with paired reads are named according to a pattern:
# {strain}_{group}_{setting}_{replica}_{reads}.fastq,
# eg. rn_wt_lg_1_R2.fastq for RN4220, wild type, logarithmic growth phase,
# replica 1 of 3, 1 of 2 files with reads. R1 and R2 are known, the remianing
# are inferred from the file names in input/reads. The number of replicas must
# be the same across all experiments (strain +  group + setting). The pipeline
# is adapted to process read for different strains, however, in the original
# case there was only one (Staphylococcus aureus RN4220, denoted as rn).
strains, groups, settings, replicas = glob_wildcards(
    'input/reads/{strain}_{group}_{setting}_{replica}_R1.fastq')

# Convert a repetetive list for a list of unique values for group and replica
groups    = list( set(groups)   )
replicas  = list( set(replicas) )

# Set the reference gropu to wt (wild type).
ref_group = 'wt'
# Library types used with Salmon (see Salom manual), the library for original
# experiment was reversed stranded with Illumina inward paired reads (ISR),
# ISF is done for antisense RNA expression analysis.
libtypes  = ['ISR', 'ISF']


# Final DGE output together with raw counts and TPM values are summarised
# for each strain, setting and library type in TSV files in output/summary.
rule all:
    input:
        expand( expand(
            'output/summary/{libtype}/summary_{strain}_{setting}.tsv',
            zip, strain=strains, setting=settings, allow_missing=True
        ), libtype=libtypes)


# Prepare index based on a FASTA file with reference transcript sequences
# for each strain with Salmon index
rule index:
    params:
        kmer = 15
    input:
        'input/refs/{strain}.fna'
    output:
        directory('output/index/{strain}')
    log:
        'log/index/{strain}.log'
    shell:
        '''salmon index -k {params.kmer} \
                        -t {input}       \
                        -i {output}      \
                         > {log} 2>&1
        '''


# Run salmon quant for each pair of read files (R1 and R2) for each strain,
# group, replica and library type, using index for the particular strain
rule quant:
    params:
        libtype = '{libtype}'
    threads:
        1
    input:
        index   = rules.index.output,
        reads_1 = 'input/reads/{strain}_{group}_{setting}_{replica}_R1.fastq',
        reads_2 = 'input/reads/{strain}_{group}_{setting}_{replica}_R2.fastq'
    output:
        directory('output/quant/{libtype}/{strain}_{group}_{setting}_{replica}')
    log:
        'log/quant/{libtype}/{strain}_{group}_{setting}_{replica}.log'
    shell:
        '''salmon quant --validateMappings  \
                        -p {threads}        \
                        -l {params.libtype} \
                        -i {input.index}    \
                        -1 {input.reads_1}  \
                        -2 {input.reads_2}  \
                        -o {output}         \
                         > {log} 2>&1
        '''


# Run the Python script scripts/collect.py to prepare metadata files that
# point to files with raw counts for all groups from the same experiment
# for a particular strain. These will be used by DESeq2.
rule collect:
    input:
        expand(rules.quant.output, libtype='{libtype}', strain='{strain}',
               group=groups, setting='{setting}', replica=replicas)
    output:
        'output/collect/{libtype}/quant_{strain}_{setting}.tsv'
    log:
        'log/collect/{libtype}/quant_{strain}_{setting}.log'
    shell:
        '''scripts/collect.py --input  {input}  \
                              --output {output} \
                                > {log} 2>&1
        '''


# Run the R script scripts/dge.r to carry out differential gene expression
# analysis with DESeq2.
rule dge:
    params:
        ref = ref_group
    input:
        rules.collect.output
    output:
        'output/dge/{libtype}/dge_{strain}_{setting}.tsv'
    log:
        'log/dge/{libtype}/dge_{strain}_{setting}.log'
    shell:
        '''scripts/dge.r --meta   {input}      \
                         --ref    {params.ref} \
                         --output {output}     \
                           > {log} 2>&1
        '''


# Collect DGE output together with raw counts and TPM values. The final stage
# of the whole pipeline.
rule summary:
    input:
        meta = rules.collect.output,
        dge  = rules.dge.output
    output:
        'output/summary/{libtype}/summary_{strain}_{setting}.tsv'
    log:
        'log/summary/{libtype}/summary_{strain}_{setting}.log'
    shell:
        '''scripts/summary.py --meta   {input.meta} \
                              --dge    {input.dge}  \
                              --output {output}     \
                                > {log} 2>&1
        '''


