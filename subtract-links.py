#! /usr/bin/env python
"""
Subtract two collections of links CSVs.
"""
import sys
import argparse
import csv

def load_links_csv(filename):
    acc_to_rows = {}
    with open(filename, 'r', newline='') as fp:
        r = csv.DictReader(fp)
        for row in r:
            acc_to_rows[row['accession']] = row

    return acc_to_rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-1', '--links-source', nargs='+', required=True,
                   help='links CSVs - source')
    p.add_argument('-2', '--links-subtract', nargs='+', required=True,
                   help='links CSVs - subtract')
    p.add_argument('-o', '--output',
                   help='output links CSV')
    p.add_argument('-f', '--force', action='store_true')
    args = p.parse_args()

    links_source = {}
    for filename in args.links_source:
        links_source.update(load_links_csv(filename))

    print(f"loaded {len(links_source)} distinct accessions from links sources.")

    links_sub = {}
    for filename in args.links_subtract:
        links_sub.update(load_links_csv(filename))

    print(f"loaded {len(links_sub)} distinct accessions from links to subtract.")

    the_source = set(links_source)
    to_sub = set(links_sub)

    if not to_sub.issubset(the_source):
        print(f"WARNING: links to subtract are not all in the source...")
        print(f"{len(to_sub - the_source)} missing - is this expected?")
        if args.force:
            print(f"continuing...")
        else:
            print(f"failing.")
            sys.exit(-1)

    keep = the_source - to_sub
    print(f"{len(keep)} accessions left after subtraction.")

    if args.output:
        with open(args.output, "w", newline='') as outfp:
            n_saved = 0
            w = csv.writer(outfp)
            w.writerow(['accession', 'name', 'taxid'])

            for acc in keep:
                row = links_source[acc]
                w.writerow([row['accession'],
                            row['name'],
                            row['taxid']])
                n_saved += 1
            print(f"saved {n_saved} rows to '{args.output}'")


if __name__ == '__main__':
    sys.exit(main())
