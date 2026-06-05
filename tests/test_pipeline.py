import unittest
from unittest.mock import Mock, patch
from src.pipeline import RedactionPipeline

class TestRedactionPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = RedactionPipeline()

    def test_english_redaction_flow(self):
        text = "Max Mustermann works at Google. Max's email is max@example.com."
        redacted = self.pipeline.redact(text)
        
        # Mappings are generated dynamically, let's verify consistent tokens are used
        self.assertIn("<NAME_1>", redacted)
        self.assertIn("<ORG_1>", redacted)
        self.assertIn("<EMAIL_1>", redacted)
        self.assertNotIn("Max Mustermann", redacted)
        self.assertNotIn("Google", redacted)
        self.assertNotIn("max@example.com", redacted)

        # Check that 'Max' is also redacted with the same token as 'Max Mustermann'
        self.assertEqual(
            redacted.replace("<NAME_1>", "NAME").replace("<ORG_1>", "ORG").replace("<EMAIL_1>", "EMAIL"),
            "NAME works at ORG. NAME's email is EMAIL."
        )

    def test_german_redaction_flow(self):
        # Starting with 'Ich' instead of 'Gestern' to prevent German spaCy sentence-start capitalization false positives.
        text = "Ich traf gestern Erika Mustermann. Erika arbeitet bei SAP und ihre Nummer ist 0170-1234567."
        redacted = self.pipeline.redact(text)

        self.assertIn("<NAME_1>", redacted)
        self.assertIn("<ORG_1>", redacted)
        self.assertIn("<PHONE_1>", redacted)
        self.assertNotIn("Erika Mustermann", redacted)
        self.assertNotIn("SAP", redacted)
        self.assertNotIn("0170-1234567", redacted)
        
        self.assertEqual(
            redacted.replace("<NAME_1>", "NAME").replace("<ORG_1>", "ORG").replace("<PHONE_1>", "PHONE"),
            "Ich traf gestern NAME. NAME arbeitet bei ORG und ihre Nummer ist PHONE."
        )

    def test_korean_redaction_flow(self):
        text = "홍길동은 서울대학교를 졸업하고 삼성전자에 입사했다. 홍길동의 이메일은 gil@samsung.com이고 전화번호는 010-1234-5678이다."
        redacted = self.pipeline.redact(text)

        # Verify tokens
        self.assertIn("<NAME_1>", redacted)
        self.assertIn("<ORG_1>", redacted)
        self.assertIn("<ORG_2>", redacted)
        self.assertIn("<EMAIL_1>", redacted)
        self.assertIn("<PHONE_1>", redacted)

        self.assertNotIn("홍길동", redacted)
        self.assertNotIn("서울대학교", redacted)
        self.assertNotIn("삼성전자", redacted)
        self.assertNotIn("gil@samsung.com", redacted)
        self.assertNotIn("010-1234-5678", redacted)

        # Replaced correctly inside particles (e.g. 홍길동은 -> <NAME_1>은)
        self.assertIn("<NAME_1>은", redacted)
        self.assertIn("<NAME_1>의", redacted)

    def test_boundary_safety(self):
        # We test _replace_entity directly to isolate word boundary behavior for ASCII
        # "Erika" should be replaced, but "Amerika" should not
        text = "Erika lives in Amerika."
        replaced = self.pipeline._replace_entity(text, "Erika", "<NAME_1>")
        self.assertEqual(replaced, "<NAME_1> lives in Amerika.")

        # Test boundary safety with alphanumeric suffix
        text2 = "Hello, Max! Is Maxwell there?"
        replaced2 = self.pipeline._replace_entity(text2, "Max", "<NAME_1>")
        self.assertEqual(replaced2, "Hello, <NAME_1>! Is Maxwell there?")

    def test_auto_detect_language(self):
        self.assertEqual(self.pipeline.detect_language("안녕하세요 홍길동입니다."), "ko")
        self.assertEqual(self.pipeline.detect_language("Das ist ein deutscher Text."), "de")
        self.assertEqual(self.pipeline.detect_language("This is a simple English paragraph."), "en")

    def test_nlp_loaders_are_lazy(self):
        pipeline = RedactionPipeline()
        self.assertIsNone(pipeline._ko_extractor)
        self.assertIsNone(pipeline._en_de_extractor)

        english_extractor = Mock()
        english_extractor.extract_entities.return_value = []
        korean_extractor = Mock()
        korean_extractor.extract_entities.return_value = []

        with patch.object(
            RedactionPipeline,
            "_load_english_german_extractor",
            return_value=english_extractor,
        ) as load_en, patch.object(
            RedactionPipeline,
            "_load_korean_extractor",
            return_value=korean_extractor,
        ) as load_ko:
            pipeline.redact("Alice works at Acme.")
            load_en.assert_called_once_with()
            load_ko.assert_not_called()
            english_extractor.extract_entities.assert_called_once()
            korean_extractor.extract_entities.assert_not_called()

        pipeline = RedactionPipeline()
        with patch.object(
            RedactionPipeline,
            "_load_english_german_extractor",
            return_value=english_extractor,
        ) as load_en, patch.object(
            RedactionPipeline,
            "_load_korean_extractor",
            return_value=korean_extractor,
        ) as load_ko:
            pipeline.redact("홍길동은 안녕하세요.")
            load_ko.assert_called_once_with()
            load_en.assert_not_called()

if __name__ == "__main__":
    unittest.main()
