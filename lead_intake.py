#!/usr/bin/env python3
"""Local lead-intake validation/deduplication demo; no network or message sending."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_CONSENT_TRUE = {"true", "yes", "1", "y"}

def norm(value):
    return str(value or "").strip()

def normalize_email(value):
    return norm(value).lower()

def normalize_phone(value):
    return re.sub(r"\D", "", norm(value))

def as_bool(value):
    if isinstance(value, bool):
        return value
    return norm(value).lower() in ALLOWED_CONSENT_TRUE

def stable_id(record):
    supplied = norm(record.get("lead_id"))
    if supplied:
        return supplied
    seed = "|".join([
        normalize_email(record.get("email")),
        normalize_phone(record.get("phone")),
        norm(record.get("company")).lower(),
        norm(record.get("name")).lower(),
        norm(record.get("source")).lower(),
    ])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

def process_records(records):
    seen_email, seen_phone, seen_id = {}, {}, {}
    queue, events = [], []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            events.append({"event":"invalid_record","row":index,"reason":"Record is not a JSON object."})
            continue
        lead_id = stable_id(record)
        name = norm(record.get("name"))
        email = normalize_email(record.get("email"))
        phone = normalize_phone(record.get("phone"))
        company = norm(record.get("company"))
        source = norm(record.get("source")) or "unspecified"
        consent = as_bool(record.get("consent_to_contact"))
        received_at = norm(record.get("received_at")) or datetime.now(timezone.utc).isoformat()
        errors = []
        if not name: errors.append("missing_name")
        if not email and not phone: errors.append("missing_contact_method")
        if email and not EMAIL_RE.match(email): errors.append("invalid_email")
        if phone and not (7 <= len(phone) <= 15): errors.append("invalid_phone")
        duplicate_of = None
        if lead_id in seen_id: duplicate_of = seen_id[lead_id]
        elif email and email in seen_email: duplicate_of = seen_email[email]
        elif phone and phone in seen_phone: duplicate_of = seen_phone[phone]
        if duplicate_of:
            status = "DUPLICATE"
            action = "Merge with the original record after human review; do not send a second follow-up."
            events.append({"event":"duplicate_detected","row":index,"lead_id":lead_id,"duplicate_of":duplicate_of,"email":email,"phone_last4":phone[-4:] if phone else ""})
        elif errors:
            status = "NEEDS_REVIEW"
            action = "Correct or confirm invalid/missing fields before any CRM write or contact."
            events.append({"event":"validation_failed","row":index,"lead_id":lead_id,"errors":errors})
        elif not consent:
            status = "HOLD_NO_CONTACT_CONSENT"
            action = "Do not send marketing or follow-up messages; verify lawful basis and recorded permissions."
            events.append({"event":"held_no_consent","row":index,"lead_id":lead_id})
        else:
            status = "READY_FOR_HUMAN_APPROVAL"
            action = "Review the inquiry and approve the next action; sending remains disabled in this demo."
            events.append({"event":"lead_ready_for_review","row":index,"lead_id":lead_id,"source":source})
            if email: seen_email[email] = lead_id
            if phone: seen_phone[phone] = lead_id
            seen_id[lead_id] = lead_id
        queue.append({
            "row":index,"lead_id":lead_id,"name":name,"email":email,
            "phone_last4":phone[-4:] if phone else "","company":company,
            "source":source,"received_at":received_at,"consent_to_contact":consent,
            "status":status,"validation_errors":";".join(errors),
            "duplicate_of":duplicate_of or "","next_action":action
        })
    counts = {}
    for item in queue: counts[item["status"]] = counts.get(item["status"],0)+1
    summary = {
        "input_records":len(records),"queue_records":len(queue),"status_counts":counts,
        "external_messages_sent":0,"external_apis_called":0,
        "note":"Demo only: all records require human review; no messages or external writes occur."
    }
    return queue, events, summary

def main():
    parser = argparse.ArgumentParser(description="Local lead-intake validation and deduplication demo.")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--queue", type=Path, default=Path("review_queue.csv"))
    parser.add_argument("--events", type=Path, default=Path("audit_events.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("summary.json"))
    args = parser.parse_args()
    try:
        records = json.loads(args.input_json.read_text(encoding="utf-8"))
        if not isinstance(records, list): raise ValueError("Input JSON must be an array.")
        queue, events, summary = process_records(records)
        args.queue.parent.mkdir(parents=True, exist_ok=True)
        fields = list(queue[0].keys()) if queue else ["row","lead_id","name","email","phone_last4","company","source","received_at","consent_to_contact","status","validation_errors","duplicate_of","next_action"]
        with args.queue.open("w",newline="",encoding="utf-8") as f:
            writer = csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(queue)
        args.events.parent.mkdir(parents=True,exist_ok=True)
        args.events.write_text("".join(json.dumps(e,ensure_ascii=False)+"\n" for e in events),encoding="utf-8")
        args.summary.parent.mkdir(parents=True,exist_ok=True)
        args.summary.write_text(json.dumps(summary,indent=2),encoding="utf-8")
        print(json.dumps(summary,indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2

if __name__ == "__main__":
    raise SystemExit(main())
