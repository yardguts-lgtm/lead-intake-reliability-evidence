# Offline sales-snapshot acceptance check | November 21, 2026

**Purpose:** Demonstrate how a buyer can independently verify that a batch of sales records actually arrived at its destination. A successful automation status is not evidence of matching records.

## Executed tests

- A new, standalone browser-based CSV checker was built locally. It requires no external service, credential, remote script, or account.
- The checker only reads two **normalized** local CSV exports. Comparison uses immutable purchase IDs and validates the customer address, UTC date, USD amount, product ID, opt-out, refund, dispute, and follow-up eligibility flags.
- The new JavaScript comparison core and simulated user-interface tests passed **33/33** on November 21, 2026.
- The inherited Python project passed **226/226** tests on the same day.
- Independent Python and JavaScript implementations agreed on two synthetic datasets:
  - PASS: 3 expected purchases, 3 destination purchases, no anomalies.
  - FAIL: 1 missing purchase, 1 unexpected purchase, 1 duplicated purchase ID, and 1 amount mismatch.
- The new browser interface was checked with JavaScript tests; a separate graphical Chromium smoke attempt timed out, so a real-browser visual acceptance check is **not claimed**.

## Limitations and safety

The checker is a **local, read-only snapshot comparator**, not a working store integration. It does not create or import destination records, access customer accounts, transmit personal data, send marketing messages, or prove future unattended transfers. A live buyer acceptance test would require the buyer's permission, actual exported records, agreed field mapping, and a fresh-post-sale replay.

The artifact is provided separately in the owner's downloadable execution package, not hosted by this repository as an interactive service. Example email domains and purchase IDs used for testing are fictional. An exported report could contain real purchase IDs when used with a customer's records; protect those reports.

## Related public technical evidence

[Earlier detailed synthetic reconciliation report](./gumroad-airtable-reconciliation-proof-2026-11-19.md)

**Commercial status:** buyer not contacted, no agreement, no paid project, and no revenue verified from this prototype.
