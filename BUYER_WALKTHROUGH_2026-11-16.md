# Buyer Walkthrough: Lead Intake Reliability

**Demonstration date:** November 16, 2026  
**Status:** Personal, synthetic-data portfolio example. Not a client deployment.

## The operating problem

Enquiries arrive from several channels. Their contact details can differ in capitalization or punctuation; entries may be duplicated; contact permission may be missing; and later replies, bookings or opt-outs must stop automated follow-up. Simply forwarding every new row creates avoidable repeat work and potentially unwanted messages.

## The bounded solution shown here

The repository provides a local Python workflow that:
1. Normalizes email/phone values and spots duplicate contacts.
2. Sends invalid or unconsented enquiries to review/hold states.
3. Produces a review queue, event ledger and summary.
4. Models follow-up approval, repeated events, replies, bookings and opt-outs as testable state transitions.
5. **Never transmits a message.** This is an offline control demonstration, not a working marketing sender.

## Live reproduction

From the repository root, with Python 3 and no external dependencies:

```sh
python3 -m unittest -v test_lead_intake test_lead_followup
```

Expected: **15 tests pass**, exit code 0. This was re-run on Xubuntu on **2026-11-16** with exit code 0.

To reproduce the eight fictional inputs without overwriting existing files:

```sh
out="$(mktemp -d)"
python3 lead_intake.py sample_leads.json --queue "$out/review.csv" --events "$out/audit.jsonl" --summary "$out/summary.json"
cat "$out/summary.json"
```

Observed on **2026-11-16**:

| Output | Count |
|---|---:|
| Fictional input records | 8 |
| Ready for human approval | 3 |
| Duplicate | 2 |
| Needs review | 2 |
| Held for missing contact permission | 1 |
| Messages transmitted | 0 |

Both the test suite and sample command exited with code 0. Counts describe *only the included fictional example*.

## How the work was coordinated

This is a **self-directed technical project**, not a claim of supervising employees or coordinating a paid client team. The work was separated into a concrete intake contract, deterministic handling rules, small test fixtures, independent test runs, dated receipts and a curated public handoff. The public demonstration was isolated from the original working local project so the original code was not changed for publication.

The handoff includes source, sample records, runnable tests, a short README and the dated test receipt. The goal is an inspectable artifact, not a polished claim about unobserved production performance.

## Application to a future customer's workflow

For an agency content queue, the same approach could **be evaluated** for duplicate client requests, missing owner/deadline fields, approval gates and stop rules. Such an adaptation would require the actual team's process and a separate test; none of those agency integrations are represented as completed here.

## Inspect the evidence

- [README and reproduction steps](README.md)
- [Sample input](sample_leads.json)
- [Intake tests](test_lead_intake.py)
- [Follow-up tests](test_lead_followup.py)
- [Previous Xubuntu test receipt](TEST_RECEIPT_2026-11-14.txt)

**Qualification limits:** No real contact information, customer systems, live integrations, paid deployment, ongoing monitoring, or production-level guarantees are claimed.
