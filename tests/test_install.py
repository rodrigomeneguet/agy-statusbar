"""Tests for install.py"""
import json
import os
import sys
from io import StringIO
from unittest.mock import patch, MagicMock, mock_open

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import install


class TestInstallMain:
    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.chmod")
    @patch("sys.stdin", new_callable=StringIO)
    def test_basic_install(self, mock_stdin, mock_chmod, mock_file, mock_copy, mock_exists):
        mock_stdin.write("n\n")
        mock_stdin.seek(0)
        mock_exists.return_value = True
        # Return different values for gemini_dir vs settings files
        mock_exists.side_effect = lambda p: True
        install.main()
        mock_copy.assert_called_once()

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_creates_gemini_dir(self, mock_exists, mock_makedirs):
        # install.py now creates dirs automatically
        with patch("shutil.copy"), patch("os.chmod"), patch("builtins.open", mock_open()):
            install.main()
        assert mock_makedirs.called

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("os.chmod")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.argv", ["install.py", "--nerd-fonts"])
    def test_nerd_fonts_flag(self, mock_file, mock_chmod, mock_copy, mock_exists):
        mock_exists.return_value = True
        install.main()
        # Check that nerdFonts was written as true
        written = mock_file().write.call_args_list
        for c in written:
            if c.args and "nerdFonts" in str(c.args[0]):
                assert "true" in str(c.args[0]).lower() or "True" in str(c.args[0])
                break

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("os.chmod")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.argv", ["install.py", "--no-nerd-fonts"])
    def test_no_nerd_fonts_flag(self, mock_file, mock_chmod, mock_copy, mock_exists):
        mock_exists.return_value = True
        install.main()

    @patch("os.path.exists")
    @patch("shutil.copy", side_effect=PermissionError("denied"))
    def test_copy_failure(self, mock_copy, mock_exists):
        mock_exists.return_value = True
        with pytest.raises(SystemExit):
            install.main()

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("os.chmod")
    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"ENABLE_NERDFONTS": "true"})
    def test_env_var_nerdfonts(self, mock_file, mock_chmod, mock_copy, mock_exists):
        mock_exists.return_value = True
        install.main()

    @patch("os.path.exists")
    @patch("shutil.copy")
    @patch("os.chmod")
    @patch("builtins.open", new_callable=mock_open)
    @patch.dict(os.environ, {"ENABLE_NERDFONTS": "false"})
    def test_env_var_no_nerdfonts(self, mock_file, mock_chmod, mock_copy, mock_exists):
        mock_exists.return_value = True
        install.main()
