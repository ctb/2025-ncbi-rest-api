#! /usr/bin/env python
"""
Do a taxon query and just save all the results to a pickle file, for use
by later scripts.
"""
import sys
import argparse
import os
from pickle import dump, load
from urllib.parse import quote

import requests
import pandas as pd

MAX_PAGE_SIZE=1000
NCBI_API_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2/"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--taxons", nargs="+", default=["2759"],
                   help="specify taxa to use for query; defaults to euks")
    p.add_argument("-o", "--save-pickle", required=True,
                   help="save resulting JSON objects to this pickle file")
    p.add_argument("--test-mode", action="store_true",
                   help="enable test mode: exit quickly")
    p.add_argument("--all-genomes",
                   action="store_true",
                   help="get all genomes, not just reference genomes")
    args = p.parse_args()

    basic_params = dict(page_size=MAX_PAGE_SIZE) # get as many results as poss.

    API_KEY = os.environ.get("NCBI_API_KEY")
    if not API_KEY:
        print(f"no API key set; use 'export NCBI_API_KEY=...' if you want.")
    else:
        print(f"NCBI API key set! :tada:")
        basic_params["api_key"] = API_KEY

    if not args.all_genomes:
        print("=> retrieving only records for reference genomes")
        basic_params["filters.reference_only"] = "true"
    else:
        print("=> getting ALL genomes because --all-genomes was specified")

    # configure taxa to query
    taxons = ",".join(args.taxons)
    print("retrieving for taxa:", taxons)
    taxons = quote(taxons)

    # get the first page
    r = requests.get(
        f"{NCBI_API_URL}/genome/taxon/{taxons}/dataset_report",
        params=basic_params,
    )
    data = r.json()

    # track all saved data in the list 'to_save'
    to_save = [data]

    while "next_page_token" in data:
        print(f"1-get-by-tax for taxa {taxons}: getting next page #{len(to_save)}")
        next_page = data["next_page_token"]

        params = dict(basic_params)  # copy params -> update with next page
        params["page_token"] = next_page

        r = requests.get(
            f"{NCBI_API_URL}/genome/taxon/{taxons}/dataset_report",
            params=params
        )
        data = r.json()
        to_save.append(data)

        if args.test_mode:  # only grab one page
            print("test mode - breaking")
            break

    print(f"1-get-by-tax for taxa {taxons}: saving ~{len(to_save)*MAX_PAGE_SIZE} results")
    with open(args.save_pickle, "wb") as fp:
        dump(to_save, fp)
        print(f"saved list of JSON objects to picklefile '{args.save_pickle}'")


if __name__ == "__main__":
    sys.exit(main())
