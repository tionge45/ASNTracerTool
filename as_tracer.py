#!/usr/bin/env python3
import sys
import subprocess
import ipaddress
import socket
from typing import List, Dict, Optional, Tuple
from utilities.exceptions import *
from utilities.network import perform_traceroute, is_valid_ip, is_private_ip
from utilities.whois import lookup_asn_info


def resolve_hostname(hostname: str) -> str:
    """Resolve hostname to IP address"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        raise HostResolutionError(f"Cannot resolve hostname: {hostname}")


def format_output(results: List[Dict]) -> str:
    """Format the results as a table"""
    header = "No. | IP Address | AS Number | Country | Provider"
    separator = "-" * len(header)
    lines = [header, separator]

    for idx, result in enumerate(results, 1):
        if result.get("error"):
            lines.append(f"{idx}. {result['ip']} - {result['error']}")
        else:
            lines.append(
                f"{idx}. | {result['ip']} | {result.get('asn', 'N/A')} | "
                f"{result.get('country', 'N/A')} | {result.get('provider', 'N/A')}"
            )

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: as_tracer.py <hostname_or_ip>")
        sys.exit(1)

    target = sys.argv[1]

    try:
        # Validate input
        if not (is_valid_ip(target) or "." in target):
            raise InvalidInputError("Please provide a valid IP address or domain name")

        # Resolve to IP if needed
        ip_target = target if is_valid_ip(target) else resolve_hostname(target)

        print(f"Tracing route to {target} ({ip_target})...\n")

        # Perform traceroute
        route_ips = perform_traceroute(ip_target)
        if not route_ips:
            print("No route information received")
            return

        # Get ASN info for each IP
        results = []
        for ip in route_ips:
            if not ip or ip == "*":
                continue

            if is_private_ip(ip):
                results.append({"ip": ip, "error": "Private IP - No ASN"})
                continue

            try:
                asn_info = lookup_asn_info(ip)
                results.append({"ip": ip, **asn_info})
            except ASNLookupError as e:
                results.append({"ip": ip, "error": str(e)})

        # Display results
        print(format_output(results))

    except NetworkError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except InvalidInputError as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTrace aborted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()