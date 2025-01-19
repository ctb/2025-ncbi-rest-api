#! /usr/bin/env python
"""
Build a sourmash lineages file from accession + taxid.

Originally written by Tessa Pierce-Ward; lightly modified by CTB.
Original at: https://github.com/bluegenes/2024-ds-plant/blob/main/taxid-to-lineages.taxonkit.py
"""
import argparse
import numpy as np
import csv
import re
import pytaxonkit


WANT_TAXONOMY = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'strain']
RANK_FORMATSTR = "{k};{p};{c};{o};{f};{g};{s};{t}" # this needs to match WANT_TAXONOMY, in format specified by taxonkit reformat cmd

 
def taxonkit_get_lineages_as_dict(taxidlist, ranks=WANT_TAXONOMY, formatstr=RANK_FORMATSTR, data_dir=None):
    # get lineage, taxpath for taxids using taxonkit
    n_failed = 0
    taxinfo = {}
    try:
        tk_lineage = pytaxonkit.lineage(taxidlist, fill_missing=True, pseudo_strain=True, formatstr=formatstr, threads=2, data_dir=data_dir) # , data_dir='.') use this to use this taxonomic data. BUT doesn't have 'strain' rank
    except Exception as e:
        print(f"ERROR: Failed to retrieve lineage data with taxonkit: {e}")
        return taxinfo, len(taxidlist)
    
    for taxid in taxidlist:
        taxid_row = tk_lineage[tk_lineage['TaxID'] == taxid]
        if not taxid_row.empty:
            try:
                lin = taxid_row.iloc[0]['Lineage']
                if lin is np.nan:
                    print(f"ERROR: taxonkit lineage for taxid {taxid} is empty")
                    print(taxid_row)
                    continue
                names = lin.split(';')
                taxpath = taxid_row.iloc[0]['LineageTaxIDs'].replace(';', '|')
            except KeyError as e:
                print(f"ERROR: KeyError for taxid {taxid}: {e}")
                print(f"taxid row: {taxid_row}")
                n_failed += 1
                continue
        else:
            names = []
            taxpath = ''
        
        n_taxids = len(taxpath.split('|'))
        if len(names) != n_taxids or len(names) != len(ranks):
            print(f"ERROR: taxonkit lineage for taxid {taxid} has mismatched lengths")
            print(f"names: {len(names)} taxids: {n_taxids} ranks: {len(ranks)}")
            n_failed += 1
            continue
        
        taxinfo[taxid] = (taxpath, names)
    
    return taxinfo, n_failed

def main(args):

    w = csv.writer(args.output)
    w.writerow(['ident', 'taxid', 'taxpath'] + WANT_TAXONOMY)

    # get the taxid from input csv #
    taxid2ident = {}
    with open(args.info, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            ident = row['accession']
            taxid = row['taxid']
            taxid2ident[int(taxid)] = ident

    # now get all lineages for the taxids
    taxid2lineage, n_fail = taxonkit_get_lineages_as_dict(taxid2ident.keys(), WANT_TAXONOMY)

    lineages_count = 0
    failed_lineages = 0
    for taxid, ident in taxid2ident.items():
        lineage = taxid2lineage.get(taxid)
        if lineage:
            taxpath, lin_names = lineage
            row = [ident, taxid, taxpath, *lin_names]
            w.writerow(row)
            lineages_count += 1
        else:
            print(f"WARNING: taxid {taxid} not in taxdump files or produced incompatible lineage. Writing empty lineage.")
            row = [ident, taxid, "", *[""] * len(WANT_TAXONOMY)]
            w.writerow(row)
            failed_lineages += 1

    failed_lineages += n_fail
    print(f"output {lineages_count} lineages")
    print(f"failed {failed_lineages} lineages")
                    

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Map numbers from one file to another based on matching IDs.')
    p.add_argument('info', help='csv with ident --> taxid mapping (CSV format)')
    p.add_argument('--data-dir', help='directory containing NCBI taxdump data (optional; default uses version associated with pytaxonkit)')
    p.add_argument('-o', '--output', help='output lineages file', type=argparse.FileType('wt'), required=True)

    args = p.parse_args()
    main(args)
