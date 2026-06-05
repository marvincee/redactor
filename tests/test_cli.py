import unittest
from unittest.mock import patch

from click.testing import CliRunner

from src.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("src.cli.write_clipboard")
    @patch("src.cli.read_clipboard", return_value="Max works at Google.")
    @patch("src.cli.RedactionPipeline")
    def test_clip_mode_redacts_and_copies(self, pipeline_cls, read_clipboard, write_clipboard):
        pipeline = pipeline_cls.return_value
        pipeline.redact.return_value = "<NAME_1> works at <ORG_1>."

        result = self.runner.invoke(main, ["--clip"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("[SUCCESS] Redacted payload copied to clipboard.", result.output)
        read_clipboard.assert_called_once_with()
        pipeline.redact.assert_called_once_with("Max works at Google.", lang=None)
        write_clipboard.assert_called_once_with("<NAME_1> works at <ORG_1>.")

    @patch("src.cli.RedactionPipeline")
    def test_text_argument_prints_redacted_output(self, pipeline_cls):
        pipeline = pipeline_cls.return_value
        pipeline.redact.return_value = "redacted text"

        result = self.runner.invoke(main, ["Max works at Google.", "--lang", "en"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output.strip(), "redacted text")
        pipeline.redact.assert_called_once_with("Max works at Google.", lang="en")

    @patch("src.cli.RedactionPipeline")
    def test_stdin_input_is_redacted(self, pipeline_cls):
        pipeline = pipeline_cls.return_value
        pipeline.redact.return_value = "redacted from stdin"

        result = self.runner.invoke(main, [], input="Max works at Google.")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output.strip(), "redacted from stdin")
        pipeline.redact.assert_called_once_with("Max works at Google.", lang=None)

    def test_clip_and_text_together_raise_usage_error(self):
        result = self.runner.invoke(main, ["Max works at Google.", "--clip"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Provide either TEXT or --clip, not both.", result.output)
