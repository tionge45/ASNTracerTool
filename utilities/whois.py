import re
import socket
import ipwhois
from ipwhois import IPWhois
from typing import Dict, Optional
from utilities.exceptions import *


def lookup_asn_info(ip: str) -> Dict[str, str]:
    """
    Lookup ASN, country and provider information for an IP address
    Returns dictionary with keys: asn, country, provider
    """
    if not ip or ip == "*":
        raise ASNLookupError("Invalid IP address")

    try:
        # Initialize IPWhois object
        ipwhois = IPWhois(ip)

        # Perform lookup with reduced timeout
        result = ipwhois.lookup_rdap(depth=1)

        # Extract relevant information
        asn = result.get('asn', '')
        asn_description = result.get('asn_description', '')
        country = result.get('asn_country_code', '')

        # Clean up ASN description
        if asn_description:
            provider = re.split(r'[,|-]', asn_description)[0].strip()
        else:
            provider = 'Unknown'

        return {
            'asn': f"AS{asn}" if asn else 'N/A',
            'country': country if country else 'N/A',
            'provider': provider
        }

    except ipwhois.exceptions.IPDefinedError:
        raise ASNLookupError("Private or reserved IP range")
    except ipwhois.exceptions.HTTPLookupError:
        raise ASNLookupError("WHOIS server lookup failed")
    except socket.timeout:
        raise ASNLookupError("WHOIS lookup timed out")
    except Exception as e:
        raise ASNLookupError(f"ASN lookup error: {str(e)}")