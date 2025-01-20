#! /usr/bin/env python
"""
Output a 'links' CSV for use by the sourmash directsketch plugin.
"""
import sys
import argparse
import os
import csv
from pickle import load
import pprint


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dataset_reports_pickle")
    p.add_argument("-o", "--save-csv", required=True)
    args = p.parse_args()

    acc_to_names = {}
    acc_to_taxid = {}

    with open(args.dataset_reports_pickle, "rb") as fp:
        results = load(fp)

    print(f"loaded {len(results)} chunks from the dataset reports pickle")

    # bad pickle?
    if "reports" not in results[0]:
        print(results)
        sys.exit(0)

    accs = []
    for chunk_num, result in enumerate(results):
        for report in result["reports"]:
            acc = report["accession"]
            org = report["organism"]
            name = org["organism_name"]
            tax_id = org["tax_id"]

            # Build a nice name
            common_name = org.get("common_name")
            if common_name:
                name = f"{common_name} ({name})"

            # Store names, accs
            accs.append(acc)
            acc_to_names[acc] = name
            acc_to_taxid[acc] = tax_id

    fp = open(args.save_csv, "w", newline="")
    w = csv.writer(fp)
    w.writerow(["accession", "name", "taxid"])
    n_written = 0

    for accession in accs:
        w.writerow(
            [
                accession,
                f"{accession} {acc_to_names[accession]}",
                acc_to_taxid[accession],
            ]
        )
        n_written += 1

    print(f"wrote {n_written} rows to '{args.save_csv}'")


if __name__ == "__main__":
    sys.exit(main())
