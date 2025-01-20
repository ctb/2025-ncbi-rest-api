#! /usr/bin/env python
"""
Make an upset plot of links CSVs.
"""
import sys
import argparse
import upsetplot
import os
import csv
from matplotlib import pyplot


def load_links_csv(filename):
    acc_to_rows = {}
    with open(filename, "r", newline="") as fp:
        r = csv.DictReader(fp)
        for row in r:
            acc_to_rows[row["accession"]] = row

    return acc_to_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("links_csvs", nargs="+")
    p.add_argument("-o", "--output", required=True, help="output figure to this file")
    args = p.parse_args()

    links_csvs = []
    for filename in args.links_csvs:
        basename = os.path.basename(filename)
        if basename.endswith(".csv"):
            basename = basename[:-4]
        if basename.endswith("-links"):
            basename = basename[:-6]

        print(f"loading {basename}")
        links_csvs.append([basename, load_links_csv(filename)])

    links_sets = [(x, set(y)) for (x, y) in links_csvs]
    memberships = dict(links_sets)

    pset = upsetplot.from_contents(memberships)
    upsetplot.plot(pset, sort_by="cardinality")
    print(f"saving plot to '{args.output}'")
    pyplot.savefig(args.output)


if __name__ == "__main__":
    sys.exit(main())
