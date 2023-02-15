#!/usr/bin/env python3
# Created by Michal Bukowski (michal.bukowski@tuta.io) under GPL-3.0 license

# This script is meant to function as a part of a Snakemake pipeline.
# Python script for preparation of metadata files that point to Salmon quant
# files for all groups from the same experiment/setting for a particular strain.

# If you find it useful, please cite:
# Bukowski M et al. (2022) Staphylococcal saoABC operon codes for
# a DNA-binding protein SaoC implicated in the response to nutrient deficit.
# International Journal of Molecular Sciences, 23(12), 6443.

import argparse, os
import pandas as pd

def parse_args():
    '''Parse arguments:
    --input  -- a list of directories with Salmon quant files
    --output -- a TSV file with metadata on biological replicas from different
                groups dedicated for one differential analysis
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument( '--input', type=str, required=True, nargs='+',
        help='List of directories with Salmon quant files')
    parser.add_argument( '--output', type=str, required=True,
        help='TSV file with metadata on biological replicas for ' +
             'differential analysis')

    args = parser.parse_args()

    return args


def run():
    '''Script entry point. Create a new Pandas DataFrame, collect the metadata,
    and save to a TSV file. The columns are:
    repname -- replica name crated as {strain}_{group}_{setting}_{replica}
    grpup -- experimantal group, groups are compared to the reference one
    fpath -- a path to a Salmon quant file containig raw counts
    '''
    args = parse_args()
    
    df = pd.DataFrame(columns=['repname', 'group', 'fpath'])

    for dir_path in args.input:
        # Values of strain, group, setting and replica are inferred from
        # directory paths.
        strain, group, setting, replica = os.path.basename(dir_path).split('_')

        df.loc[ df.shape[0] ] = dict(
            repname  = f'{strain}_{group}_{setting}_{replica}',
            group = group,
            fpath = f'{dir_path}/quant.sf'
        )

    df.to_csv(args.output, index=False, sep='\t')


if __name__ == '__main__':
    '''If not imported as a module, run the script entry function.
    '''
    run()


