# 2025-ncbi-rest-api

Use the NCBI API to grab URLs to all reference genomes under a certain
taxonomic node, and then runs the
[sourmash directsketch plugin](https://github.com/sourmash-bio/sourmash_plugin_directsketch)
on the resulting file.

To run, set your NCBI API key like so:

```
export NCBI_API_KEY=foobarbaz
```

Then, `snakemake -j 1`.
