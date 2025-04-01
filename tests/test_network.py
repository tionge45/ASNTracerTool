import subprocess

import pytest
from unittest.mock import patch, MagicMock
from utilities.network import is_valid_ip, is_private_ip, perform_traceroute
from utilities.exceptions import CommandNotFoundError, NetworkError


class TestNetworkUtils:
    @pytest.mark.parametrize("ip,expected", [
        ("8.8.8.8", True),
        ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
        ("invalid", False),
        ("256.256.256.256", False),
    ])
    def test_is_valid_ip(self, ip, expected):
        assert is_valid_ip(ip) == expected

    @pytest.mark.parametrize("ip,expected", [
        ("192.168.1.1", True),
        ("10.0.0.1", True),
        ("172.16.0.1", True),
        ("8.8.8.8", False),
        ("invalid", False),
    ])
    def test_is_private_ip(self, ip, expected):
        assert is_private_ip(ip) == expected

    @pytest.mark.parametrize("platform,command", [
        ("win32", ["tracert", "-d", "-h", "30", "-w", "2000", "8.8.8.8"]),
        ("linux", ["traceroute", "-n", "-m", "30", "-w", "2", "8.8.8.8"]),
    ])
    def test_perform_traceroute_command(self, mocker, platform, command):
        mocker.patch("sys.platform", platform)
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            b"1  192.168.1.1  10.20 ms  10.30 ms  10.40 ms",
            b"2  10.0.0.1  15.20 ms  15.30 ms  15.40 ms",
            b"3  8.8.8.8  20.20 ms  20.30 ms  20.40 ms",
            b""
        ]
        mocker.patch("subprocess.Popen", return_value=mock_process)

        result = perform_traceroute("8.8.8.8")
        assert result == ["192.168.1.1", "10.0.0.1", "8.8.8.8"]
        subprocess.Popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_perform_traceroute_timeout(self, mocker):
        mocker.patch("subprocess.Popen", side_effect=subprocess.TimeoutExpired("cmd", 10))
        with pytest.raises(NetworkError, match="Traceroute timed out"):
            perform_traceroute("8.8.8.8")

    def test_perform_traceroute_command_not_found(self, mocker):
        mocker.patch("subprocess.Popen", side_effect=FileNotFoundError)
        with pytest.raises(CommandNotFoundError):
            perform_traceroute("8.8.8.8")

    def test_perform_traceroute_with_timeouts(self, mocker):
        mocker.patch("sys.platform", "linux")
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            b"1  * * *",
            b"2  10.0.0.1  15.20 ms  15.30 ms  15.40 ms",
            b"3  * * *",
            b"4  8.8.8.8  20.20 ms  20.30 ms  20.40 ms",
            b""
        ]
        mocker.patch("subprocess.Popen", return_value=mock_process)

        result = perform_traceroute("8.8.8.8")
        assert result == [None, "10.0.0.1", None, "8.8.8.8"]