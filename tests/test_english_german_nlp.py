import unittest
from src.nlp.english_german import EnglishGermanExtractor

class TestEnglishGermanNLP(unittest.TestCase):
    def setUp(self):
        self.extractor = EnglishGermanExtractor()

    def test_extract_english_entities(self):
        text = "Alice works at Microsoft, and Bob works at Google."
        entities = self.extractor.extract_entities(text, "en")

        person_texts = [e["text"] for e in entities if e["type"] == "PERSON"]
        org_texts = [e["text"] for e in entities if e["type"] == "ORG"]

        self.assertIn("Alice", person_texts)
        self.assertIn("Bob", person_texts)
        self.assertIn("Microsoft", org_texts)
        self.assertIn("Google", org_texts)

        # Verify slices
        for ent in entities:
            self.assertEqual(text[ent["start"]:ent["end"]], ent["text"])

    def test_extract_german_entities(self):
        text = "Max Mustermann arbeitet bei SAP und Erika wohnt in Berlin."
        entities = self.extractor.extract_entities(text, "de")

        person_texts = [e["text"] for e in entities if e["type"] == "PERSON"]
        org_texts = [e["text"] for e in entities if e["type"] == "ORG"]

        self.assertIn("Max Mustermann", person_texts)
        # Note: Erika might be recognized as PERSON, Berlin is LOC (which should be skipped)
        self.assertIn("SAP", org_texts)
        self.assertNotIn("Berlin", [e["text"] for e in entities]) # Berlin is LOC/GPE, should be ignored

        # Verify slices
        for ent in entities:
            self.assertEqual(text[ent["start"]:ent["end"]], ent["text"])

    def test_empty_input(self):
        self.assertEqual(self.extractor.extract_entities("", "en"), [])
        self.assertEqual(self.extractor.extract_entities("   ", "de"), [])

if __name__ == "__main__":
    unittest.main()
