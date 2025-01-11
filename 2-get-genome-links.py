#! /usr/bin/env python
import sys
import argparse
import os
from pickle import dump, load
import time

import requests
import pandas as pd
from urllib.parse import quote

API_KEY=os.environ["NCBI_API_KEY"]


def get_links(accs):
    assert len(accs) <= 1000
    headers = {}
    basic_params = {}
    basic_params['api_key'] = API_KEY
    
    accs = quote(",".join(accs))
    r = requests.get(f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{accs}/links", params=basic_params, headers=headers)
    try:
        x = r.json()
    except:
        print(r.content)
        raise
    return x
    

def main():
    p = argparse.ArgumentParser()
    p.add_argument('dataset_reports_pickle')
    p.add_argument('-o', '--save-pickle', required=True)
    p.add_argument('--test-mode', action='store_true')
    args = p.parse_args()

    link_res = []
    acc_to_names = {}

    # load unfinished results
    if os.path.exists(args.save_pickle):
        with open(args.save_pickle, 'rb') as fp:
            link_res, acc_to_names = load(fp)
        print(f"loaded {len(acc_to_names)} successes.")

    with open(args.dataset_reports_pickle, 'rb') as fp:
        res = load(fp)

    print(f'loaded {len(res)} chunks')

    for chunk_num, r in enumerate(res):
        accs = []
        for report in r['reports']:
            acc = report['accession']
            org = report['organism']
            name = org['organism_name']
            common_name = org.get('common_name')
            if common_name:
                name = f"{common_name} ({name})"
            #print(f"{acc} {name}")
            if acc not in acc_to_names:
                accs.append(acc)
                acc_to_names[acc] = name

        for i in range(0, len(accs), 100):
            print(f'... grabbing links for {i}-{i+100} of {len(accs)} - chunk {chunk_num} of {len(res)}')
            try:
                x = get_links(accs[i:i+100])
            except:
                print('failure. punting.')
                break

            link_res.append(x)
            if args.test_mode:
                print('test mode - breaking')
                break
            time.sleep(1)

        if args.test_mode:
            print('test mode - breaking 2')

    print('saving...')
    with open(args.save_pickle, 'wb') as fp:
        dump((link_res, acc_to_names), fp)
    

if __name__ == '__main__':
    sys.exit(main())
