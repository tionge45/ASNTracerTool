from socket import socket

import pytest
from unittest.mock import patch, MagicMock
from utilities.whois import lookup_asn_info
from utilities.exceptions import ASNLookupError


class TestWhoisUtils:
    @patch('utils.whois.IPWhois')
    def test_lookup_asn_info_success(self, mock_ipwhois):
        mock_result = {
            'asn': '15169',
            'asn_description': 'GOOGLE - Google LLC, US',
            'asn_country_code': 'US'
        }
        mock_whois = MagicMock()
        mock_whois.lookup_rdap.return_value = mock_result
        mock_ipwhois.return_value = mock_whois

        result = lookup_asn_info("8.8.8.8")
        assert result == {
            'asn': 'AS15169',
            'country': 'US',
            'provider': 'GOOGLE'
        }
        mock_ipwhois.assert_called_once_with("8.8.8.8")
        mock_whois.lookup_rdap.assert_called_once_with(depth=1)

    @patch('utils.whois.IPWhois')
    def test_lookup_asn_info_private_ip(self, mock_ipwhois):
        mock_ipwhois.side_effect = Exception("Private IP")
        with pytest.raises(ASNLookupError, match="Private or reserved IP range"):
            lookup_asn_info("192.168.1.1")

    @patch('utils.whois.IPWhois')
    def test_lookup_asn_info_timeout(self, mock_ipwhois):
        mock_whois = MagicMock()
        mock_whois.lookup_rdap.side_effect = socket.timeout
        mock_ipwhois.return_value = mock_whois

        with pytest.raises(ASNLookupError, match="WHOIS lookup timed out"):
            lookup_asn_info("8.8.8.8")

    @patch('utils.whois.IPWhois')
    def test_lookup_asn_info_http_error(self, mock_ipwhois):
        mock_whois = MagicMock()
        mock_whois.lookup_rdap.side_effect = Exception("HTTP Error")
        mock_ipwhois.return_value = mock_whois

        with pytest.raises(ASNLookupError, match="ASN lookup error"):
            lookup_asn_info("8.8.8.8")

    def test_lookup_asn_info_invalid_ip(self):
        with pytest.raises(ASNLookupError, match="Invalid IP address"):
            lookup_asn_info("")