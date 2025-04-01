# Autonomous System Tracer

A tool that performs traceroute and identifies the autonomous systems (AS) for each hop.

## Features

- Performs traceroute to a target hostname or IP address
- Identifies the autonomous system (AS) for each hop
- Provides country and ISP information for each public IP
- Handles private IP addresses appropriately
- Robust error handling for network issues

## Requirements

- Python 3.6+
- `ipwhois` library
- Traceroute command (traceroute on Unix/Linux, tracert on Windows)

## Installation

```bash
pip install -r requirements.txt
````

## How to run

``` bash
python as_tracer.py <ip-address or domain name>