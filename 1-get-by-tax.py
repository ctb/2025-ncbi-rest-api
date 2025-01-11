#! /usr/bin/env python
import sys
import argparse
import os
from pickle import dump, load
from urllib.parse import quote

import requests
import pandas as pd

API_KEY=os.environ["NCBI_API_KEY"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--taxons', nargs='+', default=["2759"]) # eukaryotes
    p.add_argument('-o', '--save-pickle', required=True)
    p.add_argument('--test-mode', action='store_true')
    args = p.parse_args()

    headers = {}
    basic_params = {}
    basic_params['page_size'] = 1000
    basic_params['api_key'] = API_KEY
    basic_params['filters.reference_only'] = 'true'

    taxons = ",".join(args.taxons)
    print("retrieving for taxon(s):", taxons)
    taxons = quote(taxons)

    r = requests.get(f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxon/{taxons}/dataset_report", params=basic_params, headers=headers)
    data = r.json()

    # track all saved data
    save = [data]

    while 'next_page_token' in data:
        print(f'getting next page; have', len(save))
        next_page = data['next_page_token']
        params = dict(basic_params) # copy params -> update with next page
        params['page_token'] = next_page
        
        r = requests.get(f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxon/{taxons}/dataset_report", headers=headers, params=params)
        data = r.json()
        save.append(data)

        if args.test_mode:
            print('test mode - breaking')
            break

    page_size = basic_params['page_size']
    print(f'saving {~len(save)*page_size} results')
    with open(args.save_pickle, 'wb') as fp:
        dump(save, fp)


if __name__ == '__main__':
    sys.exit(main())
