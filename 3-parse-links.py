#! /usr/bin/env python
import sys
import argparse
import os
from pickle import dump, load
import csv


def main():
    p = argparse.ArgumentParser()
    p.add_argument('links_pickle')
    p.add_argument('-o', '--save-csv', required=True)
    args = p.parse_args()

    with open(args.links_pickle, 'rb') as fp:
        (res, acc_to_res) = load(fp)

    print('accession,name,ftp_path')
    fp = open(args.save_csv, 'w', newline='')
    w = csv.writer(fp)
    w.writerow(['accession', 'name', 'ftp_path'])
    n_written = 0

    for r in res:
        for link in r['assembly_links']:
            if link['assembly_link_type'] == 'FTP_LINK':
                accession = link['accession']
                ftp_link = link['resource_link']
                w.writerow([accession, f"{accession} {acc_to_res[accession]}", ftp_link])
                n_written += 1

    print(f"wrote {n_written}")
    

if __name__ == '__main__':
    sys.exit(main())
