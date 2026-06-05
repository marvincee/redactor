import re
from typing import Optional, TYPE_CHECKING
from src.vault import RedactionVault
from src.rules.global_rules import redact_all

if TYPE_CHECKING:
    from src.nlp.english_german import EnglishGermanExtractor
    from src.nlp.korean import KoreanExtractor

class RedactionPipeline:
    """
    Orchestrates the 3-Pass Redaction Pipeline:
    1. Pass 1 (Regex): Strips structured data (emails, phone numbers, URLs) to clean input for NLP.
    2. Pass 2 (NLP NER): Detects lang, runs spaCy/Kiwi to extract PERSON and ORG names, and registers them in the Vault.
    3. Pass 3 (Substitution): Replaces all registered entities in length-descending order, respecting word boundaries.
    """
    def __init__(self, vault: Optional[RedactionVault] = None):
        self.vault = vault if vault is not None else RedactionVault()
        self._ko_extractor: Optional["KoreanExtractor"] = None
        self._en_de_extractor: Optional["EnglishGermanExtractor"] = None

    def _load_korean_extractor(self):
        if self._ko_extractor is None:
            from src.nlp.korean import KoreanExtractor

            self._ko_extractor = KoreanExtractor()
        return self._ko_extractor

    def _load_english_german_extractor(self):
        if self._en_de_extractor is None:
            from src.nlp.english_german import EnglishGermanExtractor

            self._en_de_extractor = EnglishGermanExtractor()
        return self._en_de_extractor

    def detect_language(self, text: str) -> str:
        """Heuristically detects language: 'ko', 'de', or default 'en'."""
        # If contains Hangul, default to Korean
        if re.search(r'[\uac00-\ud7a3]', text):
            return 'ko'

        # Heuristic word list overlap for German vs English
        de_words = {"der", "die", "das", "und", "ist", "in", "zu", "den", "von", "mit", "eine", "dass", "es"}
        en_words = {"the", "and", "of", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on", "are", "as"}

        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        de_count = sum(1 for w in words if w in de_words)
        en_count = sum(1 for w in words if w in en_words)

        if de_count > en_count:
            return 'de'
        return 'en'

    def redact(self, text: str, lang: Optional[str] = None) -> str:
        """Runs the sequential 3-pass redaction process on the input text."""
        if not text.strip():
            return text

        if lang is None:
            lang = self.detect_language(text)
        else:
            lang = lang.lower()

        # --- Pass 1: Regex Redaction ---
        # Emails, phone numbers, and URLs are registered in vault and immediately replaced
        partially_redacted_text = redact_all(text, self.vault)

        # --- Pass 2: NLP NER Extraction ---
        # Extract PERSON and ORG entities from the partially redacted text
        if lang == 'ko':
            entities = self._load_korean_extractor().extract_entities(partially_redacted_text)
        else:
            entities = self._load_english_german_extractor().extract_entities(partially_redacted_text, lang)

        # Register extracted entities in the vault to generate tokens and handle name substrings
        for ent in entities:
            self.vault.get_or_create_token(ent["text"], ent["type"])

        # --- Pass 3: Substitution ---
        # Get all mappings, sort keys by length descending to avoid partial matches, and substitute
        mappings = self.vault.get_mappings()
        sorted_keys = sorted(mappings.keys(), key=len, reverse=True)

        final_text = partially_redacted_text
        for key in sorted_keys:
            token = mappings[key]
            final_text = self._replace_entity(final_text, key, token)

        return final_text

    def _replace_entity(self, text: str, key: str, token: str) -> str:
        """Replaces key with token in text, respecting word boundaries for ASCII."""
        # If key contains any CJK (Korean) characters, do direct substring replacement
        has_cjk = any(ord(char) >= 0x3000 for char in key)
        if has_cjk:
            return text.replace(key, token)

        # Otherwise, use regex with word boundary safety
        start_boundary = r'\b' if re.match(r'^\w', key) else ''
        end_boundary = r'\b' if re.search(r'\w$', key) else ''
        pattern = start_boundary + re.escape(key) + end_boundary
        return re.sub(pattern, token, text)
