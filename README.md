# Lead Intake & Follow-up Reliability | Tested Portfolio Example

A **standalone local demonstration** using Python's standard library. It processes synthetic enquiries into a review queue, normalizes contacts, handles duplicates, records decisions, and models follow-up approval/stop conditions. No messages are sent.

## Run the tests

```bash
python3 -m unittest -v test_lead_intake test_lead_followup
```

## Try the sample without modifying existing files

```bash
python3 lead_intake.py sample_leads.json --queue review.csv --events audit.jsonl --summary summary.json
```

The included data is fictional, with example-domain addresses and 555-number phones.

## What is demonstrated

- Input validation, normalized contacts and duplicate handling
- Consent hold and human review before further action
- Follow-up state management, stop rules and repeat-event handling
- Deterministic tests and auditable local results

## Limitations

This is a personal technical prototype, **not a paid-client deployment**. It does not connect to an external customer system or send messages. Test success verifies the included local cases, not performance in any third-party environment.

## Evidence

Source: an isolated, allowlisted copy of the owner's existing local workflow example. Original local project was not changed. Tested on Xubuntu on 2026-11-14; see `TEST_RECEIPT_2026-11-14.txt`.
