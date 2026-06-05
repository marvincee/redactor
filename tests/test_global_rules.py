import unittest
from src.vault import RedactionVault
from src.rules.global_rules import redact_emails, redact_phones, redact_urls, redact_all

class TestGlobalRules(unittest.TestCase):
    def setUp(self):
        self.vault = RedactionVault()

    def test_redact_emails(self):
        text = "Please contact me at max.mustermann@example.com or support@google.de."
        redacted = redact_emails(text, self.vault)
        
        self.assertIn("<EMAIL_1>", redacted)
        self.assertIn("<EMAIL_2>", redacted)
        self.assertNotIn("max.mustermann@example.com", redacted)
        self.assertNotIn("support@google.de", redacted)

        # Verify same email gets the same token
        text_same = "Write to support@google.de again."
        redacted_same = redact_emails(text_same, self.vault)
        self.assertIn("<EMAIL_2>", redacted_same)

    def test_redact_korean_phones(self):
        test_cases = [
            ("010-1234-5678", "<PHONE_1>"),
            ("+82-10-1234-5678", "<PHONE_1>"),
            ("02-123-4567", "<PHONE_1>"),
            ("010 1234 5678", "<PHONE_1>"),
            ("+82 10 1234 5678", "<PHONE_1>"),
            ("031-1234-5678", "<PHONE_1>"),
        ]
        
        for number, expected_token in test_cases:
            self.vault.clear()
            text = f"My phone number is {number}."
            redacted = redact_phones(text, self.vault)
            self.assertEqual(redacted, f"My phone number is {expected_token}.")
            self.assertEqual(self.vault.get_mappings()[number], expected_token)

    def test_redact_german_phones(self):
        test_cases = [
            ("0170 1234567", "<PHONE_1>"),
            ("+49 170 1234567", "<PHONE_1>"),
            ("030-1234-5678", "<PHONE_1>"),  # Added dash format
            ("030/12345678", "<PHONE_1>"),
            ("+49 (0)30 12345678", "<PHONE_1>"),
            ("0049 170 1234567", "<PHONE_1>"),
        ]

        for number, expected_token in test_cases:
            self.vault.clear()
            text = f"Call me at {number}."
            redacted = redact_phones(text, self.vault)
            self.assertEqual(redacted, f"Call me at {expected_token}.")
            self.assertEqual(self.vault.get_mappings()[number], expected_token)

    def test_redact_urls(self):
        test_cases = [
            ("https://google.com", "<URL_1>"),
            ("http://localhost:8080/index.html", "<URL_1>"),
            ("www.github.com/test?param=val", "<URL_1>"),
        ]

        for url, expected_token in test_cases:
            self.vault.clear()
            text = f"Visit {url} for more info."
            redacted = redact_urls(text, self.vault)
            self.assertEqual(redacted, f"Visit {expected_token} for more info.")
            self.assertEqual(self.vault.get_mappings()[url], expected_token)

    def test_no_false_positives(self):
        # Dates and large numbers should not be mistaken for phone numbers
        texts = [
            "Today's date is 2026-06-05.",
            "The ID is 123456789.",
            "There are 1000000000 reasons to be happy.",
        ]
        
        for text in texts:
            redacted = redact_phones(text, self.vault)
            self.assertEqual(redacted, text)
            self.assertEqual(len(self.vault.get_mappings()), 0)

    def test_redact_all(self):
        text = "Email max@example.com, visit https://google.com, or call +49 170 1234567."
        redacted = redact_all(text, self.vault)
        
        self.assertEqual(redacted, "Email <EMAIL_1>, visit <URL_1>, or call <PHONE_1>.")
        mappings = self.vault.get_mappings()
        self.assertEqual(mappings["max@example.com"], "<EMAIL_1>")
        self.assertEqual(mappings["https://google.com"], "<URL_1>")
        self.assertEqual(mappings["+49 170 1234567"], "<PHONE_1>")

if __name__ == "__main__":
    unittest.main()
