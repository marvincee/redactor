"""Command line interface for the local redactor."""

from __future__ import annotations

import sys

import click

from src.clipboard import ClipboardError, read_clipboard, write_clipboard
from src.pipeline import RedactionPipeline


@click.command(name="redact")
@click.argument("text", required=False)
@click.option(
    "--clip",
    is_flag=True,
    help="Read from the clipboard and write the redacted output back to it.",
)
@click.option(
    "--lang",
    type=click.Choice(["en", "de", "ko"], case_sensitive=False),
    help="Force the language pipeline instead of auto-detecting it.",
)
def main(text: str | None, clip: bool, lang: str | None) -> None:
    """Redact text from an argument, stdin, or the clipboard."""
    if clip and text is not None:
        raise click.UsageError("Provide either TEXT or --clip, not both.")

    if clip:
        try:
            source_text = read_clipboard()
        except ClipboardError as exc:
            raise click.ClickException(str(exc)) from exc
    elif text is not None:
        source_text = text
    elif not sys.stdin.isatty():
        source_text = sys.stdin.read()
    else:
        raise click.UsageError("Provide TEXT, pipe input, or use --clip.")

    pipeline = RedactionPipeline()
    redacted_text = pipeline.redact(source_text, lang=lang.lower() if lang else None)

    if clip:
        try:
            write_clipboard(redacted_text)
        except ClipboardError as exc:
            raise click.ClickException(str(exc)) from exc
        click.echo("[SUCCESS] Redacted payload copied to clipboard.")
        return

    click.echo(redacted_text)


if __name__ == "__main__":
    main()
