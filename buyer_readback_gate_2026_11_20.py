#!/usr/bin/env python3
"""Read-only CSV read-back gate. No network, no account access, no customer messages.
Compare prepared Gumroad rows with a fresh CSV export of the destination Airtable grid.
Failures omit raw purchase IDs, email addresses and cell values from reports.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

FIELDS = (
    "Purchase ID", "Purchase email", "Purchase Date UTC",
    "Product ID", "Net Total USD", "Refund Status",
    "Contact Allowed", "Follow Up State",
)
ID = "Purchase ID"


def fingerprint(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def load(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [col for col in FIELDS if col not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("missing columns: " + ", ".join(missing))
        return list(reader)


def compare(expected, observed, strict_extra=False):
    issues = []
    left, right = {}, {}
    counters = Counter()
    for side, rows, index in (("expected", expected, left), ("destination", observed, right)):
        for row in rows:
            key = (row.get(ID) or "").strip()
            if not key:
                issues.append({"kind": "blank_id", "side": side})
                continue
            if key in index:
                issues.append({"kind": "duplicate_id", "side": side, "id_hash": fingerprint(key)})
            else:
                index[key] = row
    for key, expected_row in left.items():
        identity = {"id_hash": fingerprint(key)}
        if key not in right:
            issues.append({"kind": "missing_in_destination", **identity})
            continue
        counters["found"] += 1
        actual_row = right[key]
        row_ok = True
        for field in FIELDS[1:]:
            value = (actual_row.get(field) or "").strip()
            if not value:
                issues.append({"kind": "blank_destination_value", "field": field, **identity})
                row_ok = False
            elif value != (expected_row.get(field) or "").strip():
                issues.append({"kind": "value_mismatch", "field": field, **identity})
                row_ok = False
        if row_ok:
            counters["verified"] += 1
    extra = sorted(set(right) - set(left))
    if strict_extra:
        for key in extra:
            issues.append({"kind": "unexpected_destination_row", "id_hash": fingerprint(key)})
    return {
        "status": "PASS" if not issues else "FAIL",
        "expected_unique": len(left), "destination_unique": len(right),
        "found": counters["found"], "verified": counters["verified"],
        "unrelated_destination_rows": len(extra),
        "issues": issues,
        "note": "CSV read-back only; not proof of continuous synchronization or live connection.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("expected_csv", type=Path)
    p.add_argument("destination_csv", type=Path)
    p.add_argument("--strict-extra", action="store_true")
    p.add_argument("--report", type=Path)
    a = p.parse_args()
    try:
        report = compare(load(a.expected_csv), load(a.destination_csv), a.strict_extra)
    except (ValueError, UnicodeError, OSError, csv.Error) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}))
        return 2
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if a.report:
        a.report.write_text(payload, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
