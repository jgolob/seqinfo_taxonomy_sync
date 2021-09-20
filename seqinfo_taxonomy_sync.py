#!/usr/bin/env python
import argparse
import sqlite3
import csv
from Bio import Entrez
import logging as log
import sys


def main():
    args_parser = argparse.ArgumentParser(
        description="""Tax ids can change / be retired over time.
        Confirm all tax ids in our seq info file are current.
        Correct as needed via entrez.
        """)
    args_parser.add_argument(
        'in_seqinfo', help="Input seqinfo file",
        type=argparse.FileType(mode='rt'),
        default=sys.stdin
    )

    args_parser.add_argument(
        'out_seqinfo', help="Output for corrected seqinfo file",
        type=argparse.FileType(mode='wt'),
        default=sys.stdout
    )

    args_parser.add_argument(
        '--db',
        help='Taxonomy DB path',
        required=True
    )

    args_parser.add_argument(
        '--email',
        help='Valid email (for entrez)',
        required=True
    )

    args = args_parser.parse_args()

    Entrez.email = args.email
    tax_db = sqlite3.connect(args.db)
    tax_cur = tax_db.cursor()

    seq_info = csv.DictReader(args.in_seqinfo)
    out_seq_info = csv.DictWriter(
        args.out_seqinfo,
        fieldnames=seq_info.fieldnames
    )
    out_seq_info.writeheader()
    for r in seq_info:
        tax_cur.execute("""
            SELECT COUNT(tax_id) FROM nodes
            WHERE tax_id = ?
        """, (r.get('tax_id'),))
        tax_count = tax_cur.fetchone()[0]
        if tax_count == 0:
            # Missing info for this tax ID. Almost always because it changed
            log.info("Missing {}".format(r.get('tax_id')))
            h = Entrez.efetch(
                db='taxonomy',
                id=r.get('tax_id')
            )
            tax_rec = Entrez.read(h)[0]
            new_tax_id = tax_rec.get('TaxId', 1)
            r['tax_id'] = new_tax_id
            # Confirm the NEW tax id is in the database
            tax_cur.execute("""
                    SELECT COUNT(tax_id) FROM nodes
                    WHERE tax_id = ?
                """, (new_tax_id,))
            new_tax_count = tax_cur.fetchone()[0]
            try:
                assert(new_tax_count > 0)
            except AssertionError:
                log.warning("taxonomy db is out of date, missing {}".format(new_tax_id))
        # No matter what, write a new row in our output seq info
        out_seq_info.writerow(r)

if __name__ == "__main__":
    main()
