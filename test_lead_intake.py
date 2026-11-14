import unittest
from lead_intake import process_records

class LeadIntakeTests(unittest.TestCase):
    def test_deduplicates_email_case_insensitively(self):
        q, e, s = process_records([
            {"lead_id":"1","name":"A","email":"a@example.com","consent_to_contact":True},
            {"lead_id":"2","name":"A2","email":"A@example.com","consent_to_contact":True},
        ])
        self.assertEqual(q[0]["status"], "READY_FOR_HUMAN_APPROVAL")
        self.assertEqual(q[1]["status"], "DUPLICATE")
        self.assertEqual(s["external_messages_sent"], 0)
    def test_no_consent_is_held(self):
        q, e, s = process_records([{"lead_id":"1","name":"B","email":"b@example.com","consent_to_contact":False}])
        self.assertEqual(q[0]["status"], "HOLD_NO_CONTACT_CONSENT")
    def test_invalid_contact_is_held_for_review(self):
        q, e, s = process_records([{"lead_id":"1","name":"C","email":"bad","consent_to_contact":True}])
        self.assertEqual(q[0]["status"], "NEEDS_REVIEW")
        self.assertIn("invalid_email", q[0]["validation_errors"])
    def test_duplicate_phone_is_detected(self):
        q, e, s = process_records([
            {"lead_id":"1","name":"D","phone":"+1 555 123 4567","consent_to_contact":True},
            {"lead_id":"2","name":"D2","phone":"15551234567","consent_to_contact":True},
        ])
        self.assertEqual(q[1]["status"], "DUPLICATE")

if __name__ == "__main__":
    unittest.main()
