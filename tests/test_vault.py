import unittest
from src.vault import RedactionVault

class TestRedactionVault(unittest.TestCase):
    def setUp(self):
        self.vault = RedactionVault()

    def test_consistent_token_assignment(self):
        # Exact same name should receive the exact same token
        token1 = self.vault.get_or_create_token("Max Mustermann", "PERSON")
        token2 = self.vault.get_or_create_token("Max Mustermann", "PERSON")
        self.assertEqual(token1, token2)
        self.assertEqual(token1, "<NAME_1>")

        # Different type creates a different prefix
        org_token = self.vault.get_or_create_token("Google", "ORG")
        self.assertEqual(org_token, "<ORG_1>")

    def test_substring_name_matching_longer_first(self):
        # Querying longer name first, then shorter substring name
        token_full = self.vault.get_or_create_token("Max Mustermann", "PERSON")
        token_sub = self.vault.get_or_create_token("Max", "PERSON")
        
        self.assertEqual(token_full, token_sub)
        self.assertEqual(token_full, "<NAME_1>")

        # Test another substring (surname)
        token_surname = self.vault.get_or_create_token("Mustermann", "PERSON")
        self.assertEqual(token_full, token_surname)

    def test_substring_name_matching_shorter_first(self):
        # Querying shorter name first, then longer name containing it
        token_sub = self.vault.get_or_create_token("Max", "PERSON")
        token_full = self.vault.get_or_create_token("Max Mustermann", "PERSON")
        
        self.assertEqual(token_sub, token_full)
        self.assertEqual(token_sub, "<NAME_1>")

    def test_word_boundaries_respected(self):
        # "Max" and "Maximilian" should NOT match because "Max" is not a full word in "Maximilian"
        token_max = self.vault.get_or_create_token("Max", "PERSON")
        token_maximilian = self.vault.get_or_create_token("Maximilian", "PERSON")
        
        self.assertNotEqual(token_max, token_maximilian)
        self.assertEqual(token_max, "<NAME_1>")
        self.assertEqual(token_maximilian, "<NAME_2>")

    def test_korean_substring_matching(self):
        # Korean names don't use spaces, so they require pure substring matching
        token_full = self.vault.get_or_create_token("홍길동", "PERSON")
        token_sub = self.vault.get_or_create_token("길동", "PERSON")
        
        self.assertEqual(token_full, token_sub)
        self.assertEqual(token_full, "<NAME_1>")

    def test_case_insensitivity(self):
        token1 = self.vault.get_or_create_token("Max Mustermann", "PERSON")
        token2 = self.vault.get_or_create_token("max mustermann", "PERSON")
        self.assertEqual(token1, token2)

    def test_get_mappings_returns_sorted_by_length(self):
        self.vault.get_or_create_token("Max", "PERSON")
        self.vault.get_or_create_token("Max Mustermann", "PERSON")
        
        mappings = self.vault.get_mappings()
        # Verify that both are mapped to the same token
        self.assertEqual(mappings["Max"], "<NAME_1>")
        self.assertEqual(mappings["Max Mustermann"], "<NAME_1>")

if __name__ == "__main__":
    unittest.main()
