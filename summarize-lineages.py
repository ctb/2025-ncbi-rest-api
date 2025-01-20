#! /usr/bin/env python
import argparse
import sys
from collections import defaultdict

from sourmash.tax import tax_utils


def main():
    p = argparse.ArgumentParser()
    p.add_argument("lineage_csvs", nargs="+")
    args = p.parse_args()

    unique_names = set()
    counts = defaultdict(int)

    db = tax_utils.MultiLineageDB.load(args.lineage_csvs)
    print(f"loaded {len(db)} lineage entries from {len(args.lineage_csvs)} CSVs.")

    ranks = db.available_ranks
    if "strain" in ranks:
        ranks.remove("strain")

    for ident, lineage in db.items():
        for rank, name, *rest in lineage[: len(ranks)]:
            if name not in unique_names:
                counts[rank] += 1
                unique_names.add(name)

    for rank, count in sorted(counts.items(), key=lambda x: x[1]):
        print(rank, count)


if __name__ == "__main__":
    sys.exit(main())
