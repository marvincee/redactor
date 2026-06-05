import unittest
from unittest.mock import patch

from src.clipboard import ClipboardError, read_clipboard, write_clipboard


class TestClipboard(unittest.TestCase):
    @patch("src.clipboard.subprocess.run")
    def test_read_clipboard_uses_pbpaste(self, run_mock):
        run_mock.return_value.stdout = "hello clipboard"

        result = read_clipboard()

        self.assertEqual(result, "hello clipboard")
        run_mock.assert_called_once_with(
            ["pbpaste"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("src.clipboard.subprocess.run")
    def test_write_clipboard_uses_pbcopy(self, run_mock):
        write_clipboard("hello clipboard")

        run_mock.assert_called_once_with(
            ["pbcopy"],
            check=True,
            text=True,
            input="hello clipboard",
        )

    @patch("src.clipboard.subprocess.run", side_effect=FileNotFoundError)
    def test_missing_clipboard_tools_raise_error(self, run_mock):
        with self.assertRaises(ClipboardError):
            read_clipboard()

        with self.assertRaises(ClipboardError):
            write_clipboard("hello")
