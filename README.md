# 2025-ncbi-rest-api - examples of using the NCBI Datasets API in Python

This repo contains demo and example code to use the
[NCBI Datasets REST API](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/api/rest-api/)
to grab accessions of all (reference) genomes under a certain
taxonomic node, and save/retrieve/manipulate the resulting information
for fun and profit.

The Snakefile provides a few different examples, including the use of
the
[sourmash directsketch plugin](https://github.com/sourmash-bio/sourmash_plugin_directsketch)
to download all of the genomes in bulk.

Specifically, this repo contains code to:
* Retrieve genome accessions for all eukaryotic genomes.
* Create "subtracted" lists for polyphyletic taxonomic nodes such as
  invertebrates, non-bilateria, and "other" eukaryotes.
* Download 10 fungal genome sequences.
* Retrieve NCBI lineage information for a given taxid using pytaxonkit.

and maybe more.

## Running this code

To run, set your NCBI API key like so:

```
export NCBI_API_KEY=foobarbaz
```

Create a conda environment or otherwise install the things in
`environment.yml`:

```
conda env create -n ncbi-rest-api -f environment.yml
conda activate ncbi-rest-api
```

Then:

```
snakemake -p
```

to do some basic things.

## Appendix: getting an API key

Follow [these instructions](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/api/api-keys/).

## Related repos

* https://github.com/sourmash-bio/2025-sourmash-eukaryotic-databases:
  Build eukaryotic databases for sourmash.
* https://github.com/sourmash-bio/2025-sourmash-ncbi-viral-databases:
  Build viral databases for sourmash.

## Support

I can't guarantee support for this code, of course, but odds are good
that if you find a bug or need a fix it'll be useful to me and
others. Please
[file an issue](https://github.com/ctb/2025-ncbi-rest-api/issues) with
any questions or comments! And feel free to say hi over on bluesky.

C. Titus Brown, 1/26/2025

[me on Bluesky](https://bsky.app/profile/titus.idyll.org)
