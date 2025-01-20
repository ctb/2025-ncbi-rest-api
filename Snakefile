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
#           'outputs/extra-vertebrates-links.csv'
           ]
           

# omit really large ones and already done:
# - plants
# - vertebrates
# - bilateria minus vertebrates

SKETCH_NAMES = ['fungi',
                'eukaryotes-other',
                'metazoa-minus-bilateria',
                'bilateria-minus-vertebrates',
#                'extra-bilateria-minus-vertebrates',
                ]

TEST_NAMES_TO_TAX_ID = {
    'giardia': 5740,
    'toxo': 5810,
    'diplomonads': 5738,
}
TEST_ADD_OTHER=['outputs/diplomonads-minus-giardia-links.csv']
TEST_SKETCH_NAMES = ['giardia', 'toxo']

rule default:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(NAMES_TO_TAX_ID)),
        ADD_OTHER,
        'outputs/upsetplot.png',
        'outputs/eukaryotes.lineages.csv',

rule test:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(TEST_NAMES_TO_TAX_ID)),
        TEST_ADD_OTHER,
        'outputs/test-upsetplot.png',

rule sketch:
    input:
        expand("sketches/{NAME}.sig.zip", NAME=SKETCH_NAMES),

rule test_sketch:
    input:
        expand("sketches/{NAME}.sig.zip", NAME=TEST_SKETCH_NAMES),

rule downsample:
    input:
        expand("downsampled/{NAME}.k51.s100_000.sig.zip", NAME=SKETCH_NAMES),

rule merge:
    input:
        expand("merged/{NAME}-merged.k51.s100_000.sig.zip", NAME=SKETCH_NAMES),

rule upset_plot:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(NAMES_TO_TAX_ID)),
        ADD_OTHER,
    output:
        'outputs/upsetplot.png',
    shell: """
        ./make-upset.py {input} -o {output}
    """
        
rule test_upset_plot:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(TEST_NAMES_TO_TAX_ID)),
        TEST_ADD_OTHER,
    output:
        'outputs/test-upsetplot.png',
    shell: """
        ./make-upset.py {input} -o {output}
    """

rule get_tax:
    output:
        "outputs/{NAME}-dataset-reports.pickle"
    params:
        tax_id = lambda w: { **NAMES_TO_TAX_ID, **TEST_NAMES_TO_TAX_ID}.get(w.NAME)
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

rule make_diplo_sub_csv:
    input:
        sub_from='outputs/diplomonads-links.csv',
        sub='outputs/giardia-links.csv',
    output:
        'outputs/diplomonads-minus-giardia-links.csv',
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

rule gbsketch:
    input:
        "outputs/{NAME}-links.csv",
    output:
        sigs=protected(touch("sketches/{NAME}.sig.zip")),
        check_fail="sketches/{NAME}.gbsketch-check-fail.txt",
        fail="sketches/{NAME}.gbsketch-fail.txt",
    threads: 16
    shell: """
        sourmash scripts gbsketch {input} -n 9 -r 10 -p k=21,k=31,k=51,dna \
            --failed {output.fail} --checksum-fail {output.check_fail} \
            -o {output.sigs} -c {threads} --batch 50
    """


rule downsample_sig:
    input:
        "sketches/{NAME}.sig.zip",
    output:
        "downsampled/{NAME}.k51.s100_000.sig.zip",
    shell: """
        sourmash sig downsample -k 51 -s 100_000 {input} -o {output}
    """

rule merge_sig:
    input:
        "downsampled/{NAME}.k51.s100_100.sig.zip",
    output:
        "merged/{NAME}-merged.k51.s100_100.sig.zip",
    shell: """
        sourmash sig merge -k 51 -s 100_000 {input} -o {output} \
           --set-name {wildcards.NAME}-merged
    """
