# Redactor

A fast, fully local CLI tool designed to sanitize text for LLM inputs by removing PII such as names, emails, phone numbers, and URLs.
Optimized for English, German, and Korean text.

## Core Features
* **Native clipboard integration:** Uses macOS `pbpaste` and `pbcopy` directly.
* **Consistent state:** If "Max Mustermann" is replaced with `<NAME_1>`, later mentions of "Max" also become `<NAME_1>`.
* **Multilingual pipeline:** Uses regex for structured data and lightweight NLP for human names.

## Install
If `pip` is not available on your Mac, install Python first:
```bash
brew install python
```

Then set up the project:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The first run may require the spaCy language models already available in the environment:
- `en_core_web_sm`
- `de_core_news_sm`

If they are missing, install them with:
```bash
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
```

Korean redaction uses `kiwipiepy` and requires no Java runtime.

## Usage Example
```bash
# Redact current clipboard contents
$ redact --clip

# Output:
# [SUCCESS] Redacted payload copied to clipboard.

# Redact a string directly
$ redact "Max works at Google."
```

## Platform Notes
- Clipboard support is native macOS only.
- The CLI is intentionally minimal and fast, with no background services.

## Development
```bash
python -m unittest discover -s tests
```

## Quick Start
```bash
source .venv/bin/activate
redact "Max works at Google."
redact --clip
```
