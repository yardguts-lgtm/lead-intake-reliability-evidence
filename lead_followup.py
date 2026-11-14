#!/usr/bin/env python3
"""Pure state-machine model for lead follow-up controls.

This module never sends messages or calls external services. It records workflow
state transitions so they can be tested before wiring them into n8n/WhatsApp.
"""
from __future__ import annotations

from copy import deepcopy

STOP_EVENTS = {
    "inbound_reply": "REPLIED",
    "opt_out": "OPTED_OUT",
    "consent_revoked": "OPTED_OUT",
    "booking_confirmed": "BOOKED",
    "closed": "CLOSED",
    "human_handoff": "HUMAN_HANDOFF",
}
TERMINAL_STATES = set(STOP_EVENTS.values())
VALID_STATES = {
    "WAITING_FOR_HUMAN_APPROVAL",
    "FOLLOWUP_ELIGIBLE",
    "DRAFT_READY",
    "SEND_APPROVED",
    "FOLLOWUP_SENT",
    "PAUSED",
    "HOLD_NO_CONTACT_CONSENT",
    *TERMINAL_STATES,
}


class TransitionError(ValueError):
    """Raised when an event is not valid for the current lead state."""


def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "y"}


def new_lead(lead_id: str, consent_to_contact: object) -> dict:
    if not str(lead_id or "").strip():
        raise ValueError("lead_id is required")
    consent = as_bool(consent_to_contact)
    return {
        "lead_id": str(lead_id).strip(),
        "consent_to_contact": consent,
        "state": "WAITING_FOR_HUMAN_APPROVAL" if consent else "HOLD_NO_CONTACT_CONSENT",
        "processed_event_ids": [],
        "message_sending_enabled": False,
    }


def apply_event(lead: dict, event: dict) -> tuple[dict, dict]:
    """Apply one idempotent event; return (new lead, audit result).

    Event shape: {"event_id": "...", "type": "..."}.
    A SEND_APPROVED state is only a recorded authorization state; this module
    contains no sender and cannot transmit a message.
    """
    if not isinstance(lead, dict) or lead.get("state") not in VALID_STATES:
        raise ValueError("lead has an invalid state")
    if not isinstance(event, dict):
        raise ValueError("event must be an object")

    event_id = str(event.get("event_id") or "").strip()
    event_type = str(event.get("type") or "").strip().lower()
    if not event_id:
        raise ValueError("event_id is required")
    if not event_type:
        raise ValueError("event type is required")

    updated = deepcopy(lead)
    processed = list(updated.get("processed_event_ids") or [])
    if event_id in processed:
        return updated, {
            "event_id": event_id,
            "event_type": event_type,
            "result": "DUPLICATE_EVENT_IGNORED",
            "state_before": lead["state"],
            "state_after": lead["state"],
        }

    before = updated["state"]
    if before in TERMINAL_STATES:
        processed.append(event_id)
        updated["processed_event_ids"] = processed
        return updated, {
            "event_id": event_id,
            "event_type": event_type,
            "result": "TERMINAL_STATE_NO_ACTION",
            "state_before": before,
            "state_after": before,
        }

    if event_type in STOP_EVENTS:
        after = STOP_EVENTS[event_type]
        updated["state"] = after
        if after == "OPTED_OUT":
            updated["consent_to_contact"] = False
        result = "STOP_CONDITION_APPLIED"
    elif event_type == "approve_contact":
        if before != "WAITING_FOR_HUMAN_APPROVAL":
            raise TransitionError(f"approve_contact not valid from {before}")
        if not as_bool(updated.get("consent_to_contact")):
            raise TransitionError("contact approval requires recorded consent")
        updated["state"] = "FOLLOWUP_ELIGIBLE"
        result = "CONTACT_APPROVED"
    elif event_type == "followup_due":
        if before != "FOLLOWUP_ELIGIBLE":
            raise TransitionError(f"followup_due not valid from {before}")
        if not as_bool(updated.get("consent_to_contact")):
            raise TransitionError("follow-up requires recorded consent")
        updated["state"] = "DRAFT_READY"
        result = "DRAFT_CREATED_NO_MESSAGE_SENT"
    elif event_type == "approve_send":
        if before != "DRAFT_READY":
            raise TransitionError(f"approve_send not valid from {before}")
        updated["state"] = "SEND_APPROVED"
        result = "HUMAN_SEND_APPROVAL_RECORDED_NO_MESSAGE_SENT"
    elif event_type == "outbound_sent":
        if before != "SEND_APPROVED":
            raise TransitionError(f"outbound_sent not valid from {before}")
        updated["state"] = "FOLLOWUP_SENT"
        result = "EXTERNAL_SEND_RECORDED_ONLY"
    elif event_type == "pause":
        if before not in {"FOLLOWUP_ELIGIBLE", "DRAFT_READY"}:
            raise TransitionError(f"pause not valid from {before}")
        updated["state"] = "PAUSED"
        result = "PAUSED"
    elif event_type == "resume":
        if before != "PAUSED":
            raise TransitionError(f"resume not valid from {before}")
        if not as_bool(updated.get("consent_to_contact")):
            raise TransitionError("resume requires recorded consent")
        updated["state"] = "FOLLOWUP_ELIGIBLE"
        result = "RESUMED"
    elif event_type == "consent_granted":
        if before != "HOLD_NO_CONTACT_CONSENT":
            raise TransitionError(f"consent_granted not valid from {before}")
        updated["consent_to_contact"] = True
        updated["state"] = "WAITING_FOR_HUMAN_APPROVAL"
        result = "CONSENT_RECORDED_APPROVAL_STILL_REQUIRED"
    else:
        raise TransitionError(f"unknown event type: {event_type}")

    processed.append(event_id)
    updated["processed_event_ids"] = processed
    return updated, {
        "event_id": event_id,
        "event_type": event_type,
        "result": result,
        "state_before": before,
        "state_after": updated["state"],
    }


def apply_events(lead: dict, events: list[dict]) -> tuple[dict, list[dict]]:
    current = deepcopy(lead)
    audit = []
    for event in events:
        current, result = apply_event(current, event)
        audit.append(result)
    return current, audit


def can_prepare_followup(lead: dict) -> bool:
    return (
        lead.get("state") == "FOLLOWUP_ELIGIBLE"
        and as_bool(lead.get("consent_to_contact"))
        and lead.get("message_sending_enabled") is False
    )
