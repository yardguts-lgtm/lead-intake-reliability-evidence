"""Synthetic, offline checks for buyer_readback_gate_2026_11_20.py."""
import unittest
from buyer_readback_gate_2026_11_20 import compare, fingerprint


def row(key="ORDER-1"):
    return {
        "Purchase ID": key, "Purchase email": "buyer@example.test",
        "Purchase Date UTC": "2026-11-17T00:00:00Z", "Product ID": "sku-1",
        "Net Total USD": "12.50", "Refund Status": "Paid",
        "Contact Allowed": "Review required", "Follow Up State": "Unsent / review",
    }


class ReadbackGateTests(unittest.TestCase):
    def test_clean_record_passes(self):
        self.assertEqual(compare([row()], [row()])["status"], "PASS")

    def test_missing_record_fails(self):
        self.assertEqual(compare([row()], [])["issues"][0]["kind"], "missing_in_destination")

    def test_changed_amount_fails(self):
        actual = row()
        actual["Net Total USD"] = "13.50"
        report = compare([row()], [actual])
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["issues"][0]["field"], "Net Total USD")

    def test_silent_blank_destination_cell_fails(self):
        actual = row()
        actual["Purchase email"] = ""
        self.assertEqual(compare([row()], [actual])["issues"][0]["kind"], "blank_destination_value")

    def test_duplicate_destination_id_fails(self):
        self.assertEqual(compare([row()], [row(), row()])["issues"][0]["kind"], "duplicate_id")

    def test_duplicate_source_id_fails(self):
        self.assertEqual(compare([row(), row()], [row()])["status"], "FAIL")

    def test_extra_destination_row_ignored_by_default(self):
        report = compare([row()], [row(), row("OLDER-2")])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["unrelated_destination_rows"], 1)

    def test_extra_destination_row_strict_fails(self):
        self.assertEqual(compare([row()], [row(), row("OTHER")], strict_extra=True)["status"], "FAIL")

    def test_blank_id_fails(self):
        self.assertEqual(compare([row()], [row("")])["status"], "FAIL")

    def test_no_raw_customer_values_in_failure_report(self):
        actual = row()
        actual["Purchase email"] = "private@example.test"
        report = compare([row()], [actual])
        text = str(report)
        self.assertNotIn("private@example.test", text)
        self.assertNotIn("ORDER-1", text)
        self.assertIn(fingerprint("ORDER-1"), text)

    def test_whitespace_trim_is_allowed(self):
        actual = row()
        actual["Product ID"] = " sku-1 "
        self.assertEqual(compare([row()], [actual])["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
