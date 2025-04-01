import pytest
from unittest.mock import patch, MagicMock
from as_tracer import resolve_hostname, format_output


class TestIntegration:
    @patch('socket.gethostbyname')
    def test_resolve_hostname_success(self, mock_gethostbyname):
        mock_gethostbyname.return_value = "8.8.8.8"
        assert resolve_hostname("google.com") == "8.8.8.8"

    @patch('socket.gethostbyname')
    def test_resolve_hostname_failure(self, mock_gethostbyname):
        mock_gethostbyname.side_effect = socket.gaierror
        with pytest.raises(Exception, match="Cannot resolve hostname"):
            resolve_hostname("invalid.domain")

    def test_format_output(self):
        test_data = [
            {"ip": "192.168.1.1", "error": "Private IP - No ASN"},
            {"ip": "8.8.8.8", "asn": "AS15169", "country": "US", "provider": "GOOGLE"},
            {"ip": "10.0.0.1", "error": "Lookup failed"}
        ]
        expected_output = """No. | IP Address | AS Number | Country | Provider
-------------------------------
1. 192.168.1.1 - Private IP - No ASN
2. | 8.8.8.8 | AS15169 | US | GOOGLE
3. 10.0.0.1 - Lookup failed"""

        assert format_output(test_data).strip() == expected_output.strip()

    @patch('as_tracer.perform_traceroute')
    @patch('as_tracer.lookup_asn_info')
    @patch('as_tracer.resolve_hostname')
    def test_main_success(self, mock_resolve, mock_lookup, mock_traceroute, capsys):
        mock_resolve.return_value = "8.8.8.8"
        mock_traceroute.return_value = ["192.168.1.1", "8.8.8.8"]
        mock_lookup.side_effect = [
            {"error": "Private IP - No ASN"},
            {"asn": "AS15169", "country": "US", "provider": "GOOGLE"}
        ]

        from as_tracer import main
        import sys

        sys.argv = ["as_tracer.py", "google.com"]
        main()

        captured = capsys.readouterr()
        assert "Tracing route to google.com (8.8.8.8)" in captured.out
        assert "192.168.1.1 - Private IP - No ASN" in captured.out
        assert "8.8.8.8 | AS15169 | US | GOOGLE" in captured.out