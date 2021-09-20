# seqinfo_taxonomy_sync
#
# VERSION               golob/seqinfo_taxonomy_sync:0.3.0

FROM      quay.io/biocontainers/biopython:1.78

ADD seqinfo_taxonomy_sync.py /usr/local/bin

RUN chmod +x /usr/local/bin/*.py
