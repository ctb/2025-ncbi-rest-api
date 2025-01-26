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


NCBI_API_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxon/"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--taxons", nargs="+", default=["2759"])  # eukaryotes
    p.add_argument("-o", "--save-pickle", required=True)
    p.add_argument("--test-mode", action="store_true")
    p.add_argument("--all-genomes",
                   action="store_true",
                   help="get all genomes, not just reference genomes")
    args = p.parse_args()

    API_KEY = os.environ.get("NCBI_API_KEY")
    if not API_KEY:
        assert 0, "you must set the NCBI_API_KEY environment variable"

    headers = {}
    basic_params = {}
    basic_params["page_size"] = 1000
    basic_params["api_key"] = API_KEY
    if not args.all_genomes:
        print("retrieving only records for reference genomes")
        basic_params["filters.reference_only"] = "true"
    else:
        print("getting ALL genomes because --all-genomes was specified")

    taxons = ",".join(args.taxons)
    print("retrieving for taxon(s):", taxons)
    taxons = quote(taxons)

    r = requests.get(
        f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/taxon/{taxons}/dataset_report",
        params=basic_params,
        headers=headers,
    )
    data = r.json()

    # track all saved data
    save = [data]

    while "next_page_token" in data:
        print(f"1-get-by-tax for {taxons}: getting next page; have", len(save))
        next_page = data["next_page_token"]
        params = dict(basic_params)  # copy params -> update with next page
        params["page_token"] = next_page

        r = requests.get(
            NCBI_API_URL + f"{taxons}/dataset_report", headers=headers, params=params
        )
        data = r.json()
        save.append(data)

        if args.test_mode:  # only grab one page
            print("test mode - breaking")
            break

    page_size = basic_params["page_size"]
    print(f"1-get-by-tax for {taxons}: saving ~{len(save)*page_size} results")
    with open(args.save_pickle, "wb") as fp:
        dump(save, fp)


if __name__ == "__main__":
    sys.exit(main())
