#! /usr/bin/env python
"""
Given a list of acccessions, download them all.
"""
import sys
import argparse
import os
from pickle import dump, load
from urllib.parse import quote

import requests


NCBI_API_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2/"


def main():
    p = argparse.ArgumentParser()
    p.add_argument('accessions', nargs='+')
    p.add_argument('-o', '--output', help='output zip file',
                   required=True)
    args = p.parse_args()

    basic_params = {}
    # Allowed: GENOME_GFF ┃ GENOME_GBFF ┃ GENOME_GB ┃ RNA_FASTA ┃ PROT_FASTA ┃ GENOME_GTF ┃ CDS_FASTA ┃ GENOME_FASTA ┃ SEQUENCE_REPORT
    basic_params['include_annotation_type'] = 'GENOME_FASTA'

    API_KEY = os.environ.get("NCBI_API_KEY")
    if not API_KEY:
        print(f"no API key set; use 'export NCBI_API_KEY=...' if you want.")
    else:
        print(f"NCBI API key set! :tada:")
        basic_params["api_key"] = API_KEY

    accessions = quote(",".join(args.accessions))
    r = requests.get(
        f"{NCBI_API_URL}/genome/accession/{accessions}/download",
        params=basic_params
    )
    r.raise_for_status()

    n_bytes = len(r.content)
    with open(args.output, 'wb') as fp:
        fp.write(r.content)

    print(f"wrote {n_bytes} bytes to '{args.output}'")


if __name__ == '__main__':
    sys.exit(main())
