# Sales-transfer reconciliation proof (synthetic, November 19, 2026)

This is an **offline** demonstration for a Gumroad-to-Airtable-style workflow. It does not represent a customer implementation, access to anyone's accounts, or unattended synchronization.

## Problem and acceptance contract

A successful run should not merely report that the automation ran. We need the sale records in the destination to **match the source**, exactly once each.

Acceptance compares two local CSV exports, one prepared source snapshot and one exported destination snapshot. Records match on `Purchase ID`, including customer email, UTC purchase date, sale amount, product ID, opt-out status, refund status, dispute status, and follow-up eligibility. A failed validation reports missing purchases, unexpected destination purchases, duplicated IDs, and incorrect values. Incomplete columns, unsafe IDs, ambiguous timestamps, and invalid amounts fail closed.

## Executed synthetic checks

- **PASS example:** three fictional purchases in both files; 0 missing, 0 duplicates, 0 field mismatches. Process exited successfully.
- **FAIL example:** a destination file with one missing purchase, one duplicated purchase, and one sale amount mismatch. Process exited with code 2, not a false success.
- **Regression tests:** 17 focused reconciliation tests passed on November 19, 2026; the wider local preflight, reconciliation, and opportunity-ledger selection passed 58 tests plus 2 subtests.
- **Privacy:** Runs against local sample exports, no external communication or destination writes. Sample emails use `example.test`.

## Commercial scoping

For a real buyer: agree on a small acceptance dataset, source/destination field mapping, authorized access, historical-backfill requirements, and update cadence. Test with owner-provided records; compare exported destination results to the source. Confirm the customer's chosen account plan before committing to a fully unattended workflow.

Illustrative pilot pricing: **$450 fixed, conditional on agreed scope**, not an accepted quote. A **$49/month** optional check/review is only a hypothesis.

**Important limitation:** Matching two static CSV snapshots does not prove that future sales automatically transfer. That separately requires an end-to-end, permissioned test with a new purchase and repeat-run verification.

The tested implementation and full synthetic fixtures are available as a self-contained offline delivery package; this page documents the verification result without publishing anyone's customer data.
