#!/usr/bin/env python3
# Created by Michal Bukowski (michal.bukowski@tuta.io) under GPL-3.0 license

# This script is meant to function as a part of a Snakemake pipeline.
# Python script for collecting DESeq2 DGE output together with raw counts
# and TPM values from Salmon quant files

# If you find it useful, please cite:
# Bukowski M et al. (2022) Staphylococcal saoABC operon codes for
# a DNA-binding protein SaoC implicated in the response to nutrient deficit.
# International Journal of Molecular Sciences, 23(12), 6443.

import argparse
import pandas as pd

def parse_args():
    '''Parse arguments:
    --meta   -- a TSV file with metadata on biological replicas from different
                groups dedicated for one differential analysis and generated with
                collect.py script
    --dge    -- a TSV file with DGE output data generatged with dge.r script
    --output -- the final TSV file with all data intergrated
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument( '--meta', type=str, required=True,
        help='TSV file with metadata on biological replicas for ' +
             'differential analysis')
    parser.add_argument( '--dge', type=str, required=True,
            help='Differential expression analysis results')
    parser.add_argument( '--output', type=str, required=True,
        help='TSV file summarising quantification for replicas and ' +
             'differential expression analysis results')

    args = parser.parse_args()

    return args


def run():
    '''Script entry point. Create a new Pandas DataFrame with Salmon quant data
       and DESeq2 DGE data intergated in one table.
    '''
    args = parse_args()

    # Original quant file column names.
    quant_cols = 'Name Length EffectiveLength TPM NumReads'.split()

    # Read the metadata file and DESeq2 DGE output
    df_dge  = pd.read_csv(args.dge, index_col=0, sep='\t')
    df_meta = pd.read_csv(args.meta, sep='\t')
    # Create a DataFrame for quant data for all replicas
    df_reps = [None] * df_meta.shape[0]

    # Read quant files and add column name suffixes with the group name
    # and a replica number.
    for i, (repname, group, fpath) in df_meta.iterrows():
        rep = repname.rsplit('_', 1)[-1]

        df_rep = pd.read_csv(fpath, sep='\t').rename(dict(zip(quant_cols,
            ( 'locus_tag', 'Length', f'EffectiveLength_{group}_{rep}',
             f'TPM_{group}_{rep}', f'NumReads_{group}_{rep}' )
        )), axis=1).set_index('locus_tag', drop=True)

        df_reps[i] = df_rep.drop('Length', axis=1)

    df_dge['Length'] = df_rep['Length']
    df_reps = pd.concat(df_reps, axis=1)
    df_reps.sort_index(axis=1, inplace=True)
    # Create a DataFrame for mean values from quant files for each set
    # of replicas.
    df_means = pd.DataFrame(index=df_reps.index)

    # Calculate means and them to the dedicated DataFrame
    for group in df_meta['group'].unique():
        for col in quant_cols[2:]:
            df_means[f'{col}_{group}_mean'] = df_reps.loc[
                :, df_reps.columns.str.startswith(f'{col}_{group}_')
            ].mean(axis=1)
    df_means.sort_index(axis=1, inplace=True)
    
    # Combine DESeq2 DGE data with Salmon quant data and their means, and save
    # to the final TSV output file.
    df_summary = pd.concat([df_dge, df_reps, df_means], axis=1)
    df_summary.index.name = 'locus_tag'
    df_summary.to_csv(args.output, sep='\t')


if __name__ == '__main__':
    '''If not imported as a module, run the script entry function.
    '''
    run()
