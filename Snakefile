# @CTB config-ify
#TEST_MODE="--test-mode"
TEST_MODE=""
NAME="diplomonadida"
TAX_ID="5738"
# NAME="euk"
# TAX_ID="2759"

rule all:
    input:
        f"{NAME}.sig.zip"

rule get_tax:
    output:
        f"{NAME}-dataset-reports.pickle"
    shell: """
       ./1-get-by-tax.py --taxons {TAX_ID} -o {output} {TEST_MODE}
    """


rule get_links:
    input:
        f"{NAME}-dataset-reports.pickle"
    output:
        f"{NAME}-links.pickle"
    shell: """
       ./2-get-genome-links.py {input} -o {output} {TEST_MODE}
    """

rule parse_links:
    input:
        f"{NAME}-links.pickle",
    output: 
        f"{NAME}-links.csv",
    shell: """
        ./3-parse-links.py {input} -o {output}
    """

rule gbsketch:
    input:
        f"{NAME}-links.csv",
    output:
        sigs=f"{NAME}.sig.zip",
        check_fail=f"{NAME}-check-fail.txt",
        fail=f"{NAME}-fail.txt",
    shell: """
        sourmash scripts gbsketch {input} -n 1 -p k=21,k=31,k=51,dna \
            --failed {output.fail} --checksum-fail {output.check_fail} \
            -o {output.sigs}
    """
