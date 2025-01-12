# @CTB config-ify
TEST_MODE=False

NAMES_TO_TAX_ID = {
    'eukaryotes': 2759,
    'metazoa': 33208,
    'plants': 33090,
    'fungi': 4751,
    }

SKETCH_NAMES = ['fungi']

if TEST_MODE:
    NAMES_TO_TAX_ID = {
        'giardia': 5740,
        'toxo': 5810,
        }
    SKETCH_NAMES = set(NAMES_TO_TAX_ID)
    TEST_MODE_FLAG="--test-mode"
else:
    TEST_MODE_FLAG=""

rule default:
    input:
        expand("outputs/{NAME}-links.csv", NAME=set(NAMES_TO_TAX_ID))

rule sketch:
    input:
        expand("sketches/{NAME}.sig.zip", NAME=SKETCH_NAMES)

rule get_tax:
    output:
        "outputs/{NAME}-dataset-reports.pickle"
    params:
        tax_id = lambda w: NAMES_TO_TAX_ID[w.NAME]
    shell: """
       ./1-get-by-tax.py --taxons {params.tax_id} -o {output} {TEST_MODE_FLAG}
    """


rule get_links:
    input:
        datasets="outputs/{NAME}-dataset-reports.pickle",
        round1="outputs/round1-{NAME}-links.pickle",
    output:
        "outputs/{NAME}-links.pickle"
    shell: """
       ./2-get-genome-links.py {input.datasets} -i {input.round1} -o {output} {TEST_MODE_FLAG}
    """

rule parse_links:
    input:
        "outputs/{NAME}-links.pickle",
    output: 
        "outputs/{NAME}-links.csv",
    shell: """
        ./3-parse-links.py {input} -o {output}
    """

rule gbsketch:
    input:
        "outputs/{NAME}-links.csv",
    output:
        sigs="sketches/{NAME}.sig.zip",
        check_fail="sketches/{NAME}.gbsketch-check-fail.txt",
        fail="sketches/{NAME}.gbsketch-fail.txt",
    shell: """
        sourmash scripts gbsketch {input} -n 1 -p k=21,k=31,k=51,dna \
            --failed {output.fail} --checksum-fail {output.check_fail} \
            -o {output.sigs}
    """
