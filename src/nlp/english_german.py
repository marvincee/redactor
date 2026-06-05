from typing import List, Dict, Any

class EnglishGermanExtractor:
    """
    Extracts English and German Named Entities (PERSON and ORG) from text
    using spaCy models (en_core_web_sm and de_core_news_sm).
    Standardizes labels across languages.
    """
    def __init__(self):
        self._nlp_en = None
        self._nlp_de = None

    def _get_nlp(self, lang: str):
        """Lazily loads the requested spaCy model to save startup overhead."""
        import spacy  # deferred: only paid when en/de NER is first needed
        if lang == 'en':
            if self._nlp_en is None:
                self._nlp_en = spacy.load("en_core_web_sm")
            return self._nlp_en
        elif lang == 'de':
            if self._nlp_de is None:
                self._nlp_de = spacy.load("de_core_news_sm")
            return self._nlp_de
        else:
            raise ValueError(f"Unsupported language: {lang}")

    def extract_entities(self, text: str, lang: str) -> List[Dict[str, Any]]:
        """
        Extracts PERSON and ORG entities from the text in the specified language.
        Returns a list of dicts: [{'text': str, 'start': int, 'end': int, 'type': str}]
        """
        if not text.strip():
            return []

        nlp = self._get_nlp(lang)
        doc = nlp(text)

        entities = []
        for ent in doc.ents:
            # English uses PERSON, German uses PER
            if ent.label_ in ("PERSON", "PER"):
                entities.append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "type": "PERSON"
                })
            elif ent.label_ == "ORG":
                entities.append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "type": "ORG"
                })
        return entities
