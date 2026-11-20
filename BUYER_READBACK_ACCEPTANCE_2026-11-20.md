# Gumroad to Airtable: buyer read-back verification (offline example)

Prepared November 20, 2026. Status: synthetic, read-only pre-sales evidence. No customer account accessed, no buyer application sent, and no live transfer claimed.

## Why the read-back gate matters

The [November 17 buyer](https://community.n8n.io/t/hiring-freelancer-for-airtable-workflow-remote/329131) reported a prior automation that appeared successful but didn't actually deliver results. Airtable's published documentation cautions that a row can be created even when a field value is not imported; the import's success indicator does not establish that its contents match.

The accompanying [Python verification gate](buyer_readback_gate_2026_11_20.py) compares intended purchase rows against a fresh, independently exported Airtable CSV. It checks unique Purchase ID, missing or repeated records, blank values, mismatched amounts, dates, product IDs, buyer contact restrictions and follow-up states. Reports omit raw purchase IDs and buyer emails.

Run using Python 3 and its standard library:

    python buyer_readback_gate_2026_11_20.py expected.csv destination_export.csv --report readback_report.json

Exit 0 and PASS: all expected rows match. Exit 1 and FAIL: one or more differences; do not accept delivery. Exit 2 and ERROR: unreadable file or invalid input. The optional --strict-extra flag rejects unrelated destination rows (useful for an empty new table).

Both CSV files need identical column labels: Purchase ID; Purchase email; Purchase Date UTC; Product ID; Net Total USD; Refund Status; Contact Allowed; Follow Up State. This is strict comparison, not schema conversion. Dates must be normalized before comparing. Export an unfiltered destination grid view with the required columns visible; customer permissions and ability to export must be confirmed.

Test result on November 20: 11/11 unit tests passed. A six-row synthetic destination passed; a deliberately corrupted destination with a wrong amount, blank email and repeated purchase ID failed (exit 1). This does NOT prove a live customer deployment.

## Proposed acceptance sequence

1. Agree whether amount means gross sale or seller proceeds, the refresh frequency and table fields.
2. With buyer approval, select five fictional or sanitized sample purchases and record expected rows.
3. Execute a test transfer in the buyer's real Airtable table, export the destination grid and run the gate.
4. Repeat the transfer and export to verify that replay does not create duplicate purchases.
5. Demonstrate errors, refund and no-contact restrictions, and handover instructions. No customer messaging without independent authorization.

A manual route may be more cost-effective if reports are infrequent. Airtable's CSV Import Extension is on paid plans; a **separate native third-party data import path** is available on all plan types, subject to permission and function limits. Confirm the customer's actual permissions and workflow before quoting setup costs.

## Limitations

The gate compares two CSV snapshots only. It cannot prove the export originated from Airtable, that the source was genuine, that an unattended sync works, or that a live connection exists. All examples are synthetic.

## Sources

- [Buyer request, Nov 17](https://community.n8n.io/t/hiring-freelancer-for-airtable-workflow-remote/329131)
- [Gumroad sales CSV fields](https://gumroad.com/help/article/74-the-analytics-dashboard)
- [Airtable CSV import: silently blank field values and duplicate hazards](https://support.airtable.com/articles/3067164948-csv-import-extension)
- [Airtable native import, updated Nov 4](https://support.airtable.com/articles/9412806945-importing-third-party-data-into-airtable)
- [Airtable grid CSV export](https://support.airtable.com/articles/5189551686-getting-started-with-airtable-views)
