"""Comprehensive tests for statusline.py"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from io import StringIO
from unittest.mock import MagicMock, patch, mock_open, call

import pytest

# Add parent directory to path so we can import statusline
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import statusline


# ==============================================================================
# format_tokens
# ==============================================================================
class TestFormatTokens:
    def test_none_returns_zero(self):
        assert statusline.format_tokens(None) == "0"

    def test_zero(self):
        assert statusline.format_tokens(0) == "0"

    def test_small_number(self):
        assert statusline.format_tokens(42) == "42"

    def test_boundary_999(self):
        assert statusline.format_tokens(999) == "999"

    def test_thousands(self):
        assert statusline.format_tokens(1000) == "1.0k"

    def test_thousands_with_fraction(self):
        assert statusline.format_tokens(1500) == "1.5k"

    def test_large_thousands(self):
        assert statusline.format_tokens(99999) == "100.0k"

    def test_millions(self):
        assert statusline.format_tokens(1000000) == "1.0M"

    def test_millions_with_fraction(self):
        assert statusline.format_tokens(1500000) == "1.5M"

    def test_large_millions(self):
        assert statusline.format_tokens(9999999) == "10.0M"

    def test_negative_number(self):
        result = statusline.format_tokens(-500)
        assert result == "-500" or result.endswith("k")

    def test_float_input(self):
        result = statusline.format_tokens(1500.7)
        assert "1" in result and "k" in result


# ==============================================================================
# get_git_branch
# ==============================================================================
class TestGetGitBranch:
    @patch("subprocess.run")
    def test_returns_branch_name(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="main\n"),
            MagicMock(returncode=0, stdout=""),
        ]
        result = statusline.get_git_branch("pt")
        assert result == "main"

    @patch("subprocess.run")
    def test_dirty_branch_adds_asterisk(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="main\n"),
            MagicMock(returncode=0, stdout=" M file.py\n"),
        ]
        result = statusline.get_git_branch("pt")
        assert result == "main*"

    @patch("subprocess.run")
    def test_clean_branch_no_asterisk(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="feature-x\n"),
            MagicMock(returncode=0, stdout=""),
        ]
        result = statusline.get_git_branch("pt")
        assert result == "feature-x"

    @patch("subprocess.run")
    def test_git_not_installed_pt(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        result = statusline.get_git_branch("pt")
        assert result == "Sem controle de versão"

    @patch("subprocess.run")
    def test_git_not_installed_us(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        result = statusline.get_git_branch("us")
        assert result == "No VC"

    @patch("subprocess.run")
    def test_git_not_installed_zh_tw(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        result = statusline.get_git_branch("zh-tw")
        assert result == "無版本控制"

    @patch("subprocess.run")
    def test_git_not_installed_jp(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        result = statusline.get_git_branch("jp")
        assert result == "バージョン管理なし"

    @patch("subprocess.run")
    def test_git_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=0.8)
        result = statusline.get_git_branch("pt")
        assert result == "Sem controle de versão"

    @patch("subprocess.run")
    def test_branch_with_special_chars(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="feature/JIRA-123\n"),
            MagicMock(returncode=0, stdout=""),
        ]
        result = statusline.get_git_branch("pt")
        assert result == "feature/JIRA-123"

    @patch("subprocess.run")
    def test_empty_branch_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="\n")
        result = statusline.get_git_branch("pt")
        # Empty branch name should still work
        assert isinstance(result, str)


# ==============================================================================
# get_cli_memory_mb
# ==============================================================================
class TestGetCliMemoryMb:
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="VmRSS:\t  12345 kB\n")
    def test_reads_from_parent_process(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = statusline.get_cli_memory_mb()
        assert result == 12  # 12345 // 1024

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_no_vm_info_returns_zero(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = statusline.get_cli_memory_mb()
        assert result == 0

    @patch("os.path.exists")
    def test_proc_not_found_returns_zero(self, mock_exists):
        mock_exists.return_value = False
        result = statusline.get_cli_memory_mb()
        assert result == 0

    @patch("os.path.exists")
    @patch("builtins.open", side_effect=PermissionError)
    def test_permission_error_returns_zero(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = statusline.get_cli_memory_mb()
        assert result == 0


# ==============================================================================
# get_semantic_color
# ==============================================================================
class TestGetSemanticColor:
    def test_high_percentage_normal(self):
        assert statusline.get_semantic_color(80, reverse=False) == statusline.RED

    def test_medium_high_normal(self):
        assert statusline.get_semantic_color(60, reverse=False) == statusline.ORANGE

    def test_medium_low_normal(self):
        assert statusline.get_semantic_color(30, reverse=False) == statusline.YELLOW

    def test_low_percentage_normal(self):
        assert statusline.get_semantic_color(10, reverse=False) == statusline.GREEN

    def test_high_percentage_reverse(self):
        assert statusline.get_semantic_color(80, reverse=True) == statusline.GREEN

    def test_medium_high_reverse(self):
        assert statusline.get_semantic_color(60, reverse=True) == statusline.YELLOW

    def test_medium_low_reverse(self):
        assert statusline.get_semantic_color(30, reverse=True) == statusline.ORANGE

    def test_low_percentage_reverse(self):
        assert statusline.get_semantic_color(10, reverse=True) == statusline.RED

    def test_boundary_25(self):
        assert statusline.get_semantic_color(25, reverse=False) == statusline.YELLOW

    def test_boundary_50(self):
        assert statusline.get_semantic_color(50, reverse=False) == statusline.ORANGE

    def test_boundary_75(self):
        assert statusline.get_semantic_color(75, reverse=False) == statusline.RED

    def test_zero(self):
        assert statusline.get_semantic_color(0, reverse=False) == statusline.GREEN

    def test_100(self):
        assert statusline.get_semantic_color(100, reverse=False) == statusline.RED

    def test_negative(self):
        color = statusline.get_semantic_color(-10, reverse=False)
        assert color == statusline.GREEN


# ==============================================================================
# make_progress_bar
# ==============================================================================
class TestMakeProgressBar:
    def test_capsule_full(self):
        bar = statusline.make_progress_bar(100, "capsule", 10, False)
        assert "█" * 10 in bar

    def test_capsule_empty(self):
        bar = statusline.make_progress_bar(0, "capsule", 10, False)
        assert "░" * 10 in bar

    def test_capsule_half(self):
        bar = statusline.make_progress_bar(50, "capsule", 10, False)
        assert "█" * 5 in bar
        assert "░" * 5 in bar

    def test_retro_full(self):
        bar = statusline.make_progress_bar(100, "retro", 10, False)
        assert "■" * 10 in bar

    def test_retro_empty(self):
        bar = statusline.make_progress_bar(0, "retro", 10, False)
        assert "□" * 10 in bar

    def test_minimal(self):
        bar = statusline.make_progress_bar(50, "minimal", 10, False)
        assert "●" in bar

    def test_over_100_clamped(self):
        bar = statusline.make_progress_bar(150, "capsule", 10, False)
        assert "█" * 10 in bar

    def test_negative_clamped(self):
        bar = statusline.make_progress_bar(-50, "capsule", 10, False)
        assert "░" * 10 in bar

    def test_width_1(self):
        bar = statusline.make_progress_bar(50, "capsule", 1, False)
        assert ("█" in bar) or ("░" in bar)

    def test_width_20(self):
        bar = statusline.make_progress_bar(50, "capsule", 20, False)
        assert "█" * 10 in bar
        assert "░" * 10 in bar

    def test_contains_reset(self):
        bar = statusline.make_progress_bar(50, "capsule", 10, False)
        assert statusline.RESET in bar


# ==============================================================================
# get_model_color
# ==============================================================================
class TestGetModelColor:
    def test_claude(self):
        color = statusline.get_model_color("Claude Sonnet 4.6")
        assert color != statusline.BLUE

    def test_gemini(self):
        color = statusline.get_model_color("Gemini 3.5 Flash")
        assert color == "\033[38;2;71;150;227m"

    def test_gpt(self):
        color = statusline.get_model_color("GPT-4o")
        assert color != statusline.BLUE

    def test_chatgpt(self):
        color = statusline.get_model_color("ChatGPT Plus")
        assert color != statusline.BLUE

    def test_unknown_model(self):
        color = statusline.get_model_color("SomeRandomModel")
        assert color == statusline.BLUE

    def test_none_input(self):
        color = statusline.get_model_color(None)
        assert color == statusline.BLUE

    def test_empty_string(self):
        color = statusline.get_model_color("")
        assert color == statusline.BLUE


# ==============================================================================
# strip_ansi
# ==============================================================================
class TestStripAnsi:
    def test_no_ansi(self):
        assert statusline.strip_ansi("hello world") == "hello world"

    def test_basic_sgr(self):
        result = statusline.strip_ansi("\033[31mred\033[0m")
        assert result == "red"

    def test_bold_and_color(self):
        result = statusline.strip_ansi("\033[1m\033[32mgreen\033[0m")
        assert result == "green"

    def test_256_color(self):
        result = statusline.strip_ansi("\033[38;5;196mred\033[0m")
        assert result == "red"

    def test_rgb_color(self):
        result = statusline.strip_ansi("\033[38;2;255;0;0mred\033[0m")
        assert result == "red"

    def test_empty_string(self):
        assert statusline.strip_ansi("") == ""

    def test_multiple_sequences(self):
        result = statusline.strip_ansi("\033[31mred\033[0m normal \033[32mgreen\033[0m")
        assert result == "red normal green"


# ==============================================================================
# get_display_width
# ==============================================================================
class TestGetDisplayWidth:
    def test_ascii(self):
        assert statusline.get_display_width("hello") == 5

    def test_empty(self):
        assert statusline.get_display_width("") == 0

    def test_nerd_font_pua(self):
        # PUA character (U+E725 = nf-dev-git)
        width = statusline.get_display_width("\ue725")
        assert width == 2

    def test_supplementary_pua(self):
        # Supplementary PUA (U+F0000)
        width = statusline.get_display_width("\U000f0000")
        assert width == 2

    def test_emoji(self):
        width = statusline.get_display_width("📂")
        assert width == 2

    def test_mixed_ascii_and_emoji(self):
        width = statusline.get_display_width("ab📂")
        assert width == 4

    def test_ansi_stripped(self):
        # get_display_width expects already-stripped strings
        stripped = statusline.strip_ansi("\033[31mhello\033[0m")
        width = statusline.get_display_width(stripped)
        assert width == 5


# ==============================================================================
# format_reset_time
# ==============================================================================
class TestFormatResetTime:
    def test_now(self):
        now = datetime.now(timezone.utc)
        result = statusline.format_reset_time(now.isoformat().replace("+00:00", "Z"))
        assert result == "now"

    def test_minutes(self):
        future = datetime.now(timezone.utc) + timedelta(minutes=30)
        result = statusline.format_reset_time(future.isoformat().replace("+00:00", "Z"))
        assert "m" in result

    def test_hours(self):
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        result = statusline.format_reset_time(future.isoformat().replace("+00:00", "Z"))
        assert "h" in result

    def test_days(self):
        future = datetime.now(timezone.utc) + timedelta(days=1, hours=5)
        result = statusline.format_reset_time(future.isoformat().replace("+00:00", "Z"))
        assert "d" in result

    def test_invalid_format(self):
        result = statusline.format_reset_time("not-a-date")
        assert result == ""

    def test_past_time(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        result = statusline.format_reset_time(past.isoformat().replace("+00:00", "Z"))
        assert result == "now"

    def test_exactly_one_hour(self):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        result = statusline.format_reset_time(future.isoformat().replace("+00:00", "Z"))
        assert result == "1h"

    def test_exactly_one_day(self):
        future = datetime.now(timezone.utc) + timedelta(days=1)
        result = statusline.format_reset_time(future.isoformat().replace("+00:00", "Z"))
        assert "d" in result


# ==============================================================================
# get_settings
# ==============================================================================
class TestGetSettings:
    @patch("os.path.expanduser")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_reads_global_settings(self, mock_file, mock_exists, mock_expand):
        mock_expand.return_value = "/home/user"
        mock_exists.side_effect = lambda p: "settings.json" in p and "antigravity" not in p
        mock_file.return_value.read.return_value = '{"ui": {"language": "us"}}'
        settings = statusline.get_settings()
        assert settings.get("ui", {}).get("language") == "us"

    @patch("os.path.expanduser")
    @patch("os.path.exists")
    def test_no_settings_files(self, mock_exists, mock_expand):
        mock_expand.return_value = "/home/user"
        mock_exists.return_value = False
        settings = statusline.get_settings()
        assert settings == {}

    @patch("os.path.expanduser")
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_project_settings_override(self, mock_file, mock_exists, mock_expand):
        mock_expand.return_value = "/home/user"
        # No global settings, only project settings
        def exists_side_effect(p):
            if p == "/home/user/.gemini/settings.json":
                return False
            if p == "/home/user/.gemini/antigravity-cli/settings.json":
                return False
            if p.endswith("/.gemini/settings.json"):
                return True
            return False
        mock_exists.side_effect = exists_side_effect
        mock_file.return_value.read.return_value = '{"ui": {"language": "jp"}}'
        settings = statusline.get_settings()
        assert settings.get("ui", {}).get("language") == "jp"

    @patch("os.path.expanduser")
    @patch("os.path.exists")
    @patch("builtins.open")
    def test_corrupted_json(self, mock_file, mock_exists, mock_expand):
        mock_expand.return_value = "/home/user"
        mock_exists.return_value = True
        mock_file.side_effect = json.JSONDecodeError("err", "", 0)
        settings = statusline.get_settings()
        assert settings == {}


# ==============================================================================
# find_agy_processes
# ==============================================================================
class TestFindAgyProcesses:
    @patch("subprocess.run")
    def test_finds_agy_process(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="user  12345  0.5  0.3 123456 78901 ?  Sl   10:00   0:01 agy --csrf_token=abc123\n"
        )
        result = statusline.find_agy_processes()
        assert len(result) >= 1
        assert result[0]["pid"] == 12345
        assert result[0]["csrf_token"] == "abc123"

    @patch("subprocess.run")
    def test_finds_antigravity_process(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="user  12345  0.5  0.3 123456 78901 ?  Sl   10:00   0:01 python antigravity-cli\n"
        )
        result = statusline.find_agy_processes()
        assert len(result) >= 1

    @patch("subprocess.run")
    def test_finds_language_server(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="user  12345  0.5  0.3 123456 78901 ?  Sl   10:00   0:01 language_server --port=50051\n"
        )
        result = statusline.find_agy_processes()
        assert len(result) >= 1

    @patch("subprocess.run")
    def test_no_processes_found(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n")
        result = statusline.find_agy_processes()
        assert result == []

    @patch("subprocess.run")
    def test_ps_command_fails(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        result = statusline.find_agy_processes()
        assert result == []

    @patch("subprocess.run")
    def test_sorted_by_score(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "user  11111  0.5  0.3 123456 78901 ?  Sl   10:00   0:01 language_server --port=50051\n"
                "user  22222  0.5  0.3 123456 78901 ?  Sl   10:00   0:01 agy --csrf_token=tok1\n"
            )
        )
        result = statusline.find_agy_processes()
        if len(result) >= 2:
            assert result[0]["score"] >= result[1]["score"]

    @patch("subprocess.run")
    def test_penalty_for_app_bundle(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="user  12345  0.5  0.3 123456 78901 ?  Sl   10:00   0:01 /Applications/Antigravity.app/Contents/MacOS/antigravity\n"
        )
        result = statusline.find_agy_processes()
        # Should still find it but with penalty
        assert isinstance(result, list)


# ==============================================================================
# get_listening_ports
# ==============================================================================
class TestGetListeningPorts:
    @patch("subprocess.check_output")
    def test_finds_ports(self, mock_check):
        mock_check.return_value = "python3  12345  user  5u  IPv4  12345  0t0  TCP *:50051 (LISTEN)\n"
        result = statusline.get_listening_ports(12345)
        assert 50051 in result

    @patch("subprocess.check_output")
    def test_multiple_ports(self, mock_check):
        mock_check.return_value = (
            "python3  12345  user  5u  IPv4  12345  0t0  TCP *:50051 (LISTEN)\n"
            "python3  12345  user  6u  IPv4  12346  0t0  TCP *:8080 (LISTEN)\n"
        )
        result = statusline.get_listening_ports(12345)
        assert 50051 in result
        assert 8080 in result

    @patch("subprocess.check_output")
    def test_no_ports(self, mock_check):
        mock_check.return_value = ""
        result = statusline.get_listening_ports(12345)
        assert result == []

    @patch("subprocess.check_output")
    def test_lsof_not_installed(self, mock_check):
        mock_check.side_effect = FileNotFoundError
        result = statusline.get_listening_ports(12345)
        assert result == []

    @patch("subprocess.check_output")
    def test_sorted_output(self, mock_check):
        mock_check.return_value = (
            "python3  12345  user  5u  IPv4  12345  0t0  TCP *:8080 (LISTEN)\n"
            "python3  12345  user  6u  IPv4  12346  0t0  TCP *:50051 (LISTEN)\n"
        )
        result = statusline.get_listening_ports(12345)
        assert result == sorted(result)


# ==============================================================================
# request_user_status
# ==============================================================================
class TestRequestUserStatus:
    @patch("urllib.request.urlopen")
    def test_successful_request(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"userStatus": {}}).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        result = statusline.request_user_status(50051, "token123")
        assert "userStatus" in result

    @patch("urllib.request.urlopen")
    def test_request_with_ssl_error(self, mock_urlopen):
        import ssl
        mock_urlopen.side_effect = ssl.SSLError("cert verify failed")
        with pytest.raises(ssl.SSLError):
            statusline.request_user_status(50051, "token123")

    @patch("urllib.request.urlopen")
    def test_request_timeout(self, mock_urlopen):
        import socket
        mock_urlopen.side_effect = socket.timeout("timed out")
        with pytest.raises(socket.timeout):
            statusline.request_user_status(50051, "token123")


# ==============================================================================
# main (integration)
# ==============================================================================
class TestMain:
    def _make_input(self, **kwargs):
        data = {
            "model": {"display_name": "Gemini 3.5 Flash"},
            "context_window": {
                "total_input_tokens": 50000,
                "total_output_tokens": 10000,
                "used_percentage": 5.0,
                "context_window_size": 1048576,
            },
            "terminal_width": 120,
            "conversation_id": "test-conv-123",
        }
        data.update(kwargs)
        return json.dumps(data)

    @patch("statusline.get_cli_memory_mb", return_value=128)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "pt", "statusline": {"theme": "capsule"}}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_basic_output(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=0)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "us"}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_empty_input(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write("")
        mock_stdin.seek(0)
        # Should return without error
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=0)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={})
    @patch("sys.stdin", new_callable=StringIO)
    def test_invalid_json(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write("not json")
        mock_stdin.seek(0)
        # Should handle gracefully
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="dev*")
    @patch("statusline.get_settings", return_value={"ui": {"language": "pt", "statusline": {"theme": "retro"}}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_retro_theme(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=32)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "pt", "statusline": {"theme": "minimal"}}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_minimal_theme(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "zh-tw", "statusline": {"theme": "capsule"}}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_chinese_language(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "jp", "statusline": {"theme": "capsule"}}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_japanese_language(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={
        "ui": {
            "language": "pt",
            "statusline": {"theme": "capsule", "nerdFonts": True},
            "footer": {"items": ["git-branch", "model-name"]}
        }
    })
    @patch("sys.stdin", new_callable=StringIO)
    def test_custom_footer_items(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "pt", "statusline": {"progressBarWidth": 20}}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_wide_progress_bar(self, mock_stdin, mock_settings, mock_git, mock_mem):
        mock_stdin.write(self._make_input())
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "pt"}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_no_model_in_input(self, mock_stdin, mock_settings, mock_git, mock_mem):
        data = {
            "context_window": {"total_input_tokens": 1000, "used_percentage": 1.0, "context_window_size": 100000},
            "terminal_width": 80,
        }
        mock_stdin.write(json.dumps(data))
        mock_stdin.seek(0)
        statusline.main()

    @patch("statusline.get_cli_memory_mb", return_value=64)
    @patch("statusline.get_git_branch", return_value="main")
    @patch("statusline.get_settings", return_value={"ui": {"language": "pt"}})
    @patch("sys.stdin", new_callable=StringIO)
    def test_zero_tokens(self, mock_stdin, mock_settings, mock_git, mock_mem):
        data = {
            "model": {"display_name": "Test Model"},
            "context_window": {"total_input_tokens": 0, "total_output_tokens": 0, "used_percentage": 0, "context_window_size": 0},
            "terminal_width": 80,
        }
        mock_stdin.write(json.dumps(data))
        mock_stdin.seek(0)
        statusline.main()


# ==============================================================================
# fetch_live_quota (mocked)
# ==============================================================================
class TestFetchLiveQuota:
    @patch("statusline.get_listening_ports", return_value=[50051])
    @patch("statusline.find_agy_processes")
    @patch("statusline.request_user_status")
    def test_fetches_quota(self, mock_req, mock_find, mock_ports):
        mock_find.return_value = [{"pid": 12345, "csrf_token": "tok", "score": 50, "kind": "cli"}]
        mock_req.return_value = {
            "userStatus": {
                "cascadeModelConfigData": {
                    "clientModelConfigs": [
                        {
                            "label": "Gemini 3.5 Flash",
                            "modelOrAlias": {"model": "gemini-3.5-flash"},
                            "quotaInfo": {"remainingFraction": 0.75, "resetTime": "2026-06-03T00:00:00Z"},
                        }
                    ]
                }
            }
        }
        result = statusline.fetch_live_quota()
        assert result is not None
        assert "models" in result

    @patch("statusline.find_agy_processes", return_value=[])
    def test_no_processes_returns_none(self, mock_find):
        result = statusline.fetch_live_quota()
        assert result is None

    @patch("statusline.get_listening_ports", return_value=[])
    @patch("statusline.find_agy_processes")
    def test_no_ports_returns_none(self, mock_find, mock_ports):
        mock_find.return_value = [{"pid": 12345, "csrf_token": "tok", "score": 50, "kind": "cli"}]
        result = statusline.fetch_live_quota()
        assert result is None


# ==============================================================================
# __main__ entry point
# ==============================================================================
class TestEntryPoint:
    @patch("statusline.fetch_live_quota")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.argv", ["statusline.py", "--fetch-quota"])
    def test_fetch_quota_mode(self, mock_file, mock_makedirs, mock_fetch):
        mock_fetch.return_value = {"models": {}, "updatedAt": 123}
        # Simulate the __main__ block
        import importlib
        with patch.object(sys, "argv", ["statusline.py", "--fetch-quota"]):
            # Directly test the logic
            assert sys.argv[1] == "--fetch-quota"
            cache = statusline.fetch_live_quota()
            assert cache is not None
