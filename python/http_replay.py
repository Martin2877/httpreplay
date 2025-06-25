#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import signal
import sys
import argparse
from scapy.all import *
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import json

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(b"HTTP Replay Server is running. Send POST requests to /replay to start replaying.")

def start_http_server(port=8000):
    """Start a simple HTTP server to handle replay requests."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"HTTP server started on port {port}")
    httpd.serve_forever()

def replay_http_requests(pcap_file, target_url, interface=None, count=1, delay=1):
    """
    Replay HTTP requests from a PCAP file to a target URL.
    
    Args:
        pcap_file (str): Path to the PCAP file containing HTTP requests
        target_url (str): Target URL to replay requests to
        interface (str): Network interface to use (default: None for default interface)
        count (int): Number of times to replay the requests (default: 1)
        delay (float): Delay between requests in seconds (default: 1)
    """
    try:
        # Read the PCAP file
        packets = rdpcap(pcap_file)
        http_requests = []
        
        # Extract HTTP requests from PCAP
        for pkt in packets:
            if pkt.haslayer('Raw'):
                try:
                    http_layer = pkt['Raw'].load.decode('utf-8', errors='ignore')
                    if 'HTTP' in http_layer and 'GET' in http_layer:
                        http_requests.append(http_layer)
                except:
                    continue
        
        if not http_requests:
            print("No HTTP requests found in the PCAP file.")
            return
        
        print(f"Found {len(http_requests)} HTTP requests in the PCAP file.")
        
        # Replay the requests
        for i in range(count):
            print(f"\nReplay iteration {i+1}/{count}")
            for j, req in enumerate(http_requests):
                try:
                    # Parse the request
                    lines = req.split('\r\n')
                    method, path, _ = lines[0].split(' ', 2)
                    headers = {}
                    body = None
                    
                    # Parse headers
                    for line in lines[1:]:
                        if not line.strip():
                            break
                        if ':' in line:
                            key, value = line.split(':', 1)
                            headers[key.strip()] = value.strip()
                    
                    # Parse body if present
                    if '\r\n\r\n' in req:
                        body = req.split('\r\n\r\n', 1)[1]
                    
                    # Build the target URL
                    full_url = f"{target_url.rstrip('/')}{path}"
                    
                    # Make the request
                    print(f"Request {j+1}: {method} {full_url}")
                    
                    # You can use requests library for more complex scenarios
                    # For simplicity, we'll use curl here
                    cmd = ['curl', '-X', method, full_url]
                    for key, value in headers.items():
                        cmd.extend(['-H', f"{key}: {value}"])
                    if body:
                        cmd.extend(['-d', body])
                    
                    # Execute the request
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    print(f"Status: {result.returncode}")
                    
                    # Add delay between requests
                    if j < len(http_requests) - 1:
                        time.sleep(delay)
                        
                except Exception as e:
                    print(f"Error processing request {j+1}: {str(e)}")
                    continue
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    return True

def capture_http_traffic(interface, output_file, duration=30, filter_expr="tcp port 80 or tcp port 443"):
    """
    Capture HTTP/HTTPS traffic to a PCAP file.
    
    Args:
        interface (str): Network interface to capture on (e.g., 'eth0', 'en0')
        output_file (str): Output PCAP file path
        duration (int): Duration to capture in seconds (default: 30)
        filter_expr (str): BPF filter expression (default: "tcp port 80 or tcp port 443")
    """
    print(f"Starting capture on interface {interface} for {duration} seconds...")
    print(f"Filter: {filter_expr}")
    print(f"Output file: {output_file}")
    
    try:
        # Start tshark to capture traffic
        cmd = [
            'tshark',
            '-i', interface,
            '-w', output_file,
            '-a', f'duration:{duration}',
            '-f', filter_expr
        ]
        
        print("\nCapturing traffic (press Ctrl+C to stop early)...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for the capture to complete or until interrupted
        try:
            process.wait(timeout=duration + 5)
        except subprocess.TimeoutExpired:
            process.terminate()
            print("Capture completed.")
        
        print(f"\nTraffic capture saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error during capture: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='HTTP Replay and Capture Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Replay command
    replay_parser = subparsers.add_parser('replay', help='Replay HTTP requests from a PCAP file')
    replay_parser.add_argument('-i', '--input', required=True, help='Input PCAP file')
    replay_parser.add_argument('-t', '--target', required=True, help='Target URL')
    replay_parser.add_argument('-I', '--interface', help='Network interface')
    replay_parser.add_argument('-c', '--count', type=int, default=1, help='Number of times to replay')
    replay_parser.add_argument('-d', '--delay', type=float, default=1, help='Delay between requests in seconds')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture HTTP traffic to a PCAP file')
    capture_parser.add_argument('-i', '--interface', required=True, help='Network interface to capture on')
    capture_parser.add_argument('-o', '--output', required=True, help='Output PCAP file')
    capture_parser.add_argument('-d', '--duration', type=int, default=30, help='Duration to capture in seconds')
    capture_parser.add_argument('-f', '--filter', default='tcp port 80 or tcp port 443', 
                              help='BPF filter expression (default: tcp port 80 or tcp port 443)')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start HTTP server for API access')
    server_parser.add_argument('-p', '--port', type=int, default=8000, help='Port to listen on')
    
    args = parser.parse_args()
    
    if args.command == 'replay':
        replay_http_requests(
            args.input,
            args.target,
            interface=args.interface,
            count=args.count,
            delay=args.delay
        )
    elif args.command == 'capture':
        capture_http_traffic(
            args.interface,
            args.output,
            duration=args.duration,
            filter_expr=args.filter
        )
    elif args.command == 'server':
        print(f"Starting HTTP server on port {args.port}")
        start_http_server(port=args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
