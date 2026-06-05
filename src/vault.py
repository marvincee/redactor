import re
from typing import Dict

class RedactionVault:
    """
    A translation ledger that maintains consistent redaction tokens for entities
    within a single execution run. It handles exact matching and dynamic substring
    matching (e.g., resolving 'Max' to the same token as 'Max Mustermann').
    """
    def __init__(self):
        # Mappings of exact string -> token (e.g. {"Max Mustermann": "<NAME_1>"})
        self.mappings: Dict[str, str] = {}
        # Keep track of target entity types for mapped strings
        self.types: Dict[str, str] = {}
        # Counter state for each token prefix type
        self.counters: Dict[str, int] = {
            "NAME": 1,
            "ORG": 1,
            "EMAIL": 1,
            "PHONE": 1,
            "URL": 1,
        }

    def _get_prefix(self, entity_type: str) -> str:
        """Standardizes the entity type into a token prefix."""
        upper_type = entity_type.upper()
        if upper_type in ("PERSON", "NAME"):
            return "NAME"
        if upper_type == "ORG":
            return "ORG"
        if upper_type in ("EMAIL", "EMAIL_ADDRESS"):
            return "EMAIL"
        if upper_type in ("PHONE", "PHONE_NUMBER"):
            return "PHONE"
        if upper_type in ("URL", "LINK"):
            return "URL"
        return upper_type

    def _names_match(self, name1: str, name2: str) -> bool:
        """
        Determines whether two name strings should be considered matching variants.
        Supports case-insensitivity, word boundaries for space-separated names,
        and substring matching for languages without space separation (like Korean).
        """
        n1 = name1.strip().lower()
        n2 = name2.strip().lower()
        if not n1 or not n2:
            return False
        if n1 == n2:
            return True

        short_name, long_name = (n1, n2) if len(n1) < len(n2) else (n2, n1)

        # Check if the long name contains CJK (Chinese/Japanese/Korean) characters.
        # Korean Hangul Syllables range from 0xAC00 to 0xD7A3.
        has_cjk = any(ord(char) >= 0x3000 for char in long_name)
        if has_cjk:
            return short_name in long_name

        # Word boundary match for space-separated languages
        pattern = rf"\b{re.escape(short_name)}\b"
        return bool(re.search(pattern, long_name))

    def get_or_create_token(self, entity_name: str, entity_type: str) -> str:
        """
        Retrieves an existing token for the entity name or generates a new one.
        Uses substring and word-boundary rules to match variants of names.
        """
        name_clean = entity_name.strip()
        if not name_clean:
            return ""

        prefix = self._get_prefix(entity_type)

        # 1. Try exact (case-insensitive) match first
        for existing_name, token in self.mappings.items():
            if existing_name.lower() == name_clean.lower():
                return token

        # 2. Try substring match (only within the same standardized category)
        for existing_name, token in self.mappings.items():
            existing_prefix = self._get_prefix(self.types[existing_name])
            if existing_prefix == prefix:
                if self._names_match(existing_name, name_clean):
                    # Register this variant as well so subsequent lookups are O(1)
                    self.mappings[name_clean] = token
                    self.types[name_clean] = entity_type
                    return token

        # 3. Create a new token if no match is found
        count = self.counters.get(prefix, 1)
        token = f"<{prefix}_{count}>"
        self.counters[prefix] = count + 1

        self.mappings[name_clean] = token
        self.types[name_clean] = entity_type
        return token

    def get_mappings(self) -> Dict[str, str]:
        """Returns the dictionary of all name -> token mappings."""
        return self.mappings

    def clear(self):
        """Resets the ledger state."""
        self.mappings.clear()
        self.types.clear()
        for k in self.counters:
            self.counters[k] = 1
