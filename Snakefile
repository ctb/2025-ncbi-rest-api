# @CTB config-ify
TEST_MODE=False

NAMES_TO_TAX_ID = {
    'eukaryotes': 2759,
    'metazoa': 33208,
    'plants': 33090,
    'fungi': 4751,
    'bilateria': 33213,
    'vertebrates': 7742,
    }

ADD_OTHER=['outputs/bilateria-minus-vertebrates-links.csv',
           'outputs/metazoa-minus-bilateria-links.csv']

SKETCH_NAMES = ['fungi', 'euk-other', 'metazoa-100.2']

if TEST_MODE:
    NAMES_TO_TAX_ID = {
        'giardia': 5740,
        'toxo': 5810,
        'diplomonads': 5738,
        }
    SKETCH_NAMES = set(NAMES_TO_TAX_ID)
    ADD_OTHER=['outputs/diplomonads-minus-giardia-links.csv']

rule default:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(NAMES_TO_TAX_ID)),
        ADD_OTHER,

rule sketch:
    input:
        expand("sketches/{NAME}.sig.zip", NAME=SKETCH_NAMES)

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

rule gbsketch:
    input:
        "outputs/{NAME}-links.csv",
    output:
        sigs=protected("sketches/{NAME}.sig.zip"),
        check_fail="sketches/{NAME}.gbsketch-check-fail.txt",
        fail="sketches/{NAME}.gbsketch-fail.txt",
    shell: """
        sourmash scripts gbsketch {input} -n 5 -p k=21,k=31,k=51,dna \
            --failed {output.fail} --checksum-fail {output.check_fail} \
            -o {output.sigs}
    """
