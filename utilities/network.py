import re
import subprocess
import ipaddress
import sys
import time
from typing import List, Optional
from utilities.exceptions import *


def is_valid_ip(ip_str: str) -> bool:
    """Check if the input is a valid IP address"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def is_private_ip(ip_str: str) -> bool:
    """Check if IP is in private range"""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private
    except ValueError:
        return False


def perform_traceroute(target: str, max_hops: int = 30, timeout: int = 2) -> List[Optional[str]]:
    """
    Perform traceroute and return list of IP addresses
    Handles both Windows (tracert) and Unix (traceroute) systems
    """
    ips = []

    if not is_valid_ip(target):
        raise InvalidInputError("Invalid target IP address")

    if sys.platform.startswith('win'):
        command = ['tracert', '-d', '-h', str(max_hops), '-w', str(timeout * 1000), target]
    else:
        command = ['traceroute', '-n', '-m', str(max_hops), '-w', str(timeout), target]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            line = process.stdout.readline()
            if not line:
                break

            line = line.decode('utf-8', errors='ignore').strip()

            # Parse line for IP address
            ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            if ip_match:
                ip = ip_match.group(0)
                if ip != target and ip not in ips:
                    ips.append(ip)
            elif '*' in line:
                ips.append(None)

    except FileNotFoundError:
        raise CommandNotFoundError("traceroute/tracert command not found")
    except subprocess.TimeoutExpired:
        process.kill()
        raise NetworkError("Traceroute timed out")
    except Exception as e:
        raise NetworkError(f"Traceroute failed: {str(e)}")

    return ips