#! /usr/bin/env python
"""
Compare links_csvs and sketch databases, optionally saving missing links
to a new file and/or creating manifests of matching sketches.
"""
import sys
import argparse
import csv
import os.path

import sourmash
from sourmash.sourmash_args import SaveSignaturesToLocation
from sourmash.picklist import SignaturePicklist
from sourmash.manifest import CollectionManifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--links-csvs", nargs="+", required=True, help="links CSVs")
    p.add_argument(
        "--sigs", nargs="+", required=True, help="sourmash sketches/databases"
    )
    p.add_argument(
        "--save-missing-links", help="save links entries not present to this CSV"
    )
    p.add_argument(
        "--save-matching-to-manifest",
        help="make a standalone manifest containing the sketches matching to the links",
    )
    args = p.parse_args()

    acc_to_links = {}
    for filename in args.links_csvs:
        with open(filename, "r", newline="") as fp:
            r = csv.DictReader(fp)
            for row in r:
                acc_to_links[row["accession"]] = row

    print(f"loaded {len(acc_to_links)} distinct accessions from links CSVs.")

    acc_to_sketchname = {}
    for dbname in args.sigs:
        db = sourmash.load_file_as_index(dbname)
        mf = db.manifest
        for row in mf.rows:
            name = row["name"]
            ident = name.split(" ")[0]
            acc_to_sketchname[ident] = name

    print(f"loaded {len(acc_to_sketchname)} distinct accessions from sigs.")

    sketch_accs = set(acc_to_sketchname)
    link_accs = set(acc_to_links)
    common = link_accs.intersection(sketch_accs)

    print(f"{len(common)} accessions in common.")
    print(f"{len(sketch_accs - link_accs)} only in sketches.")
    print(f"{len(link_accs - sketch_accs)} only in links.")

    if args.save_missing_links:
        with open(args.save_missing_links, "w", newline="") as outfp:
            w = csv.writer(outfp)
            n_saved = 0

            w.writerow(["accession", "name", "taxid"])
            for acc in link_accs - sketch_accs:
                row = acc_to_links[acc]
                w.writerow([row["accession"], row["name"], row["taxid"]])
                n_saved += 1

            print(f"saved {n_saved} rows to '{args.save_missing_links}'")

    if args.save_matching_to_manifest:
        pl = SignaturePicklist("ident")
        pl.init(common)

        rows = []
        for dbname in args.sigs:
            print(f"loading from sigfile '{dbname}'")
            db = sourmash.load_file_as_index(dbname)
            db = db.select(picklist=pl)
            iloc = os.path.abspath(dbname)

            mf = db.manifest
            for row in mf.rows:
                row["internal_location"] = iloc
                rows.append(row)

        mf = CollectionManifest(rows)
        mf.write_to_filename(
            args.save_matching_to_manifest, ok_if_exists=True, database_format="csv"
        )
        print(f"wrote {len(mf)} manifest rows to '{args.save_matching_to_manifest}'")


if __name__ == "__main__":
    sys.exit(main())
