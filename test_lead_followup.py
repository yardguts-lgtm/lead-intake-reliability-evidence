import unittest

from lead_followup import (
    TransitionError,
    apply_event,
    apply_events,
    can_prepare_followup,
    new_lead,
)


def ev(event_id, event_type):
    return {"event_id": event_id, "type": event_type}


class LeadFollowupTests(unittest.TestCase):
    def test_no_consent_is_held(self):
        lead = new_lead("L-1", False)
        self.assertEqual(lead["state"], "HOLD_NO_CONTACT_CONSENT")
        self.assertFalse(can_prepare_followup(lead))

    def test_approval_required_before_draft(self):
        lead = new_lead("L-2", True)
        with self.assertRaises(TransitionError):
            apply_event(lead, ev("e1", "followup_due"))
        lead, _ = apply_event(lead, ev("e2", "approve_contact"))
        self.assertTrue(can_prepare_followup(lead))
        lead, result = apply_event(lead, ev("e3", "followup_due"))
        self.assertEqual(lead["state"], "DRAFT_READY")
        self.assertEqual(result["result"], "DRAFT_CREATED_NO_MESSAGE_SENT")
        self.assertFalse(lead["message_sending_enabled"])

    def test_send_approval_does_not_send_message(self):
        lead = new_lead("L-3", True)
        lead, _ = apply_events(lead, [ev("e1", "approve_contact"), ev("e2", "followup_due")])
        lead, result = apply_event(lead, ev("e3", "approve_send"))
        self.assertEqual(lead["state"], "SEND_APPROVED")
        self.assertEqual(result["result"], "HUMAN_SEND_APPROVAL_RECORDED_NO_MESSAGE_SENT")
        self.assertFalse(lead["message_sending_enabled"])

    def test_inbound_reply_stops_followup(self):
        lead = new_lead("L-4", True)
        lead, _ = apply_event(lead, ev("e1", "approve_contact"))
        lead, _ = apply_event(lead, ev("e2", "inbound_reply"))
        self.assertEqual(lead["state"], "REPLIED")
        lead, result = apply_event(lead, ev("e3", "followup_due"))
        self.assertEqual(lead["state"], "REPLIED")
        self.assertEqual(result["result"], "TERMINAL_STATE_NO_ACTION")

    def test_opt_out_revokes_consent_and_stops(self):
        lead = new_lead("L-5", True)
        lead, _ = apply_event(lead, ev("e1", "approve_contact"))
        lead, _ = apply_event(lead, ev("e2", "opt_out"))
        self.assertEqual(lead["state"], "OPTED_OUT")
        self.assertFalse(lead["consent_to_contact"])

    def test_booking_stops_followup(self):
        lead = new_lead("L-6", True)
        lead, _ = apply_event(lead, ev("e1", "approve_contact"))
        lead, _ = apply_event(lead, ev("e2", "booking_confirmed"))
        self.assertEqual(lead["state"], "BOOKED")

    def test_closed_and_human_handoff_are_terminal(self):
        for index, event_type, expected in [
            (7, "closed", "CLOSED"),
            (8, "human_handoff", "HUMAN_HANDOFF"),
        ]:
            lead = new_lead(f"L-{index}", True)
            lead, _ = apply_event(lead, ev(f"e-{index}", "approve_contact"))
            lead, _ = apply_event(lead, ev(f"stop-{index}", event_type))
            self.assertEqual(lead["state"], expected)

    def test_duplicate_event_is_idempotent(self):
        lead = new_lead("L-9", True)
        lead, first = apply_event(lead, ev("same-id", "approve_contact"))
        lead, second = apply_event(lead, ev("same-id", "approve_contact"))
        self.assertEqual(first["result"], "CONTACT_APPROVED")
        self.assertEqual(second["result"], "DUPLICATE_EVENT_IGNORED")
        self.assertEqual(lead["state"], "FOLLOWUP_ELIGIBLE")

    def test_terminal_state_cannot_be_reopened(self):
        lead = new_lead("L-10", True)
        lead, _ = apply_event(lead, ev("e1", "opt_out"))
        lead, result = apply_event(lead, ev("e2", "approve_contact"))
        self.assertEqual(lead["state"], "OPTED_OUT")
        self.assertEqual(result["result"], "TERMINAL_STATE_NO_ACTION")

    def test_consent_grant_still_requires_human_approval(self):
        lead = new_lead("L-11", False)
        lead, result = apply_event(lead, ev("e1", "consent_granted"))
        self.assertEqual(lead["state"], "WAITING_FOR_HUMAN_APPROVAL")
        self.assertEqual(result["result"], "CONSENT_RECORDED_APPROVAL_STILL_REQUIRED")
        with self.assertRaises(TransitionError):
            apply_event(lead, ev("e2", "followup_due"))

    def test_event_id_is_required(self):
        lead = new_lead("L-12", True)
        with self.assertRaises(ValueError):
            apply_event(lead, {"type": "approve_contact"})


if __name__ == "__main__":
    unittest.main()
