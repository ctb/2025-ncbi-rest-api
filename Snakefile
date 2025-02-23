NAMES_TO_TAX_ID = {
    'eukaryotes': 2759,
    'metazoa': 33208,
    'plants': 33090,
    'fungi': 4751,
    'bilateria': 33213,
    'vertebrates': 7742,
    }

ADD_OTHER=['outputs/bilateria-minus-vertebrates-links.csv',
           'outputs/metazoa-minus-bilateria-links.csv',
           'outputs/eukaryotes-other-links.csv',
           ]
           
# pull down the various nodes in NAMES_TO_TAX_ID, build a lineages CSV file,
# and download 10 fungal genomes; also download a single data set file.
rule default:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(NAMES_TO_TAX_ID)),
        'outputs/eukaryotes.lineages.csv',
        'genomes/fungi-top10.d',
        'GCF_963082475.1.dataset.zip',

rule download_dataset:
    output:
        'GCF_963082475.1.dataset.zip',
    shell: """
        ./1-download-genome.py GCF_963082475.1 -o {output}
    """

# retrieve all reference genomes under node => build a pickle file
# containing that info.
rule get_tax:
    output:
        "outputs/{NAME}-dataset-reports.pickle"
    params:
        tax_id = lambda w: NAMES_TO_TAX_ID[w.NAME]
    shell: """
       ./1-get-by-tax.py --taxons {params.tax_id} -o {output}
    """

rule parse_links:
    input:
        datasets="outputs/{NAME}-dataset-reports.pickle",
    output: 
        "outputs/{NAME}-links.csv",
    shell: """
        ./2-output-directsketch-csv.py {input} -o {output}
    """

rule lineages_csv:
    input:
        "outputs/{NAME}-links.csv",
    output:
        "outputs/{NAME}.lineages.csv",
    shell: """
        ./taxid-to-lineages.taxonkit.py {input} -o {output}
    """

rule make_invertebrates_csv:
    input:
        sub_from='outputs/bilateria-links.csv',
        sub='outputs/vertebrates-links.csv',
    output:
        'outputs/bilateria-minus-vertebrates-links.csv',
    shell: """
        ./subtract-links.py -1 {input.sub_from} \
            -2 {input.sub} -o {output}
    """

rule make_metazoa_sub_bilateria_csv:
    input:
        sub_from='outputs/metazoa-links.csv',
        sub='outputs/bilateria-links.csv',
    output:
        'outputs/metazoa-minus-bilateria-links.csv',
    shell: """
        ./subtract-links.py -1 {input.sub_from} \
            -2 {input.sub} -o {output}
    """

rule eukaryotes_other_csv:
    input:
        sub_from='outputs/eukaryotes-links.csv',
        sub=['outputs/metazoa-links.csv',
             'outputs/plants-links.csv',
             'outputs/fungi-links.csv',
             ]
    output:
        'outputs/eukaryotes-other-links.csv',
    shell: """
        ./subtract-links.py -1 {input.sub_from} \
            -2 {input.sub} -o {output}
    """

rule fungi_top10:
    input:
        "outputs/fungi-links.csv",
    output:
        "outputs/fungi-top10-links.csv",
    shell: "head -11 {input} > {output}"

rule directsketch_download:
    input:
        "outputs/{name}-links.csv",
    output:
        dir=directory("genomes/{name}.d/"),
        failed="genomes/fail-{name}.txt",
        checkfail="genomes/checkfail-{name}.txt",
    shell: """
       sourmash scripts gbsketch --download-only --keep-fasta --genomes-only \
          {input} -f {output.dir}
    """
