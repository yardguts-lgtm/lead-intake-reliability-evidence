# Gumroad → Airtable: sales-export reliability proof (synthetic candidate)

**Prepared:** 2026-11-18  
**Status:** Local demonstration only. Not a tested live Gumroad or Airtable connection; not a completed client project. No customer data or messages used.

## Why this sample exists

A public November 17 buyer request asks for purchase email, transaction date, amount and product ID from Gumroad sales to be recorded accurately in Airtable. It explicitly describes an earlier implementation that appeared to work but did not. Any paid implementation must prove delivery inside the buyer's actual destination, not just show a screenshot of a diagram.

## Testable acceptance criteria for a small paid trial

1. Confirm the buyer's purchase fields and table structure.
2. Enter at least five fictional or sanitized purchases and verify matching records in the buyer's Airtable table.
3. Reprocess records and demonstrate no duplicate purchase IDs.
4. Produce visible exceptions for invalid data or conflicting repeated IDs.
5. Mark refunded, disputed and opt-out purchases as held from customer follow-up.
6. Deliver a readable verification report and recovery steps before asking for acceptance.

## Synthetic offline exercise (13/13 tests passed)

A Python standard-library prototype was run on 2026-11-18 using 10 fictional rows shaped around documented Gumroad CSV export fields:

| Outcome | Count |
|---|---:|
| Unique processed purchases | 6 |
| Identical duplicate skipped | 1 |
| Conflicting duplicate sent for manual review | 1 |
| Invalid rows flagged | 2 |
| Processed records held from follow-up | 4 |

A reproducible local sample, test suite, generated import-ready CSV, exception report and checksums are retained in the buyer-acquisition evidence package. No real purchases were synchronized.

Important: Gumroad's documented export uses UTC purchase dates and includes an explicit **Do not contact** flag. This prototype preserves these protections. Airtable's CSV Import Extension is restricted to paid plans as of 2026-09-14. That manual import path is not an always-on synchronization service. Its merge key, when available, should be purchase ID, not buyer email.

## Public related work

For inspectable Python/SQLite intake reliability code and testing, see this repository's main branch: [lead-intake-reliability-evidence](https://github.com/yardguts-lgtm/lead-intake-reliability-evidence).

This buyer-specific proof is only an **independent pre-sales exercise**, not proof of professional prior delivery or guaranteed suitability.

## References

- Buyer request (2026-11-17): https://community.n8n.io/t/hiring-freelancer-for-airtable-workflow-remote/329131
- Gumroad sales CSV fields and UTC notes: https://gumroad.com/help/article/74-the-analytics-dashboard
- Airtable CSV import documentation and paid-plan availability: https://support.airtable.com/articles/3067164948-csv-import-extension
