#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import argparse
import time
import os
import uuid
import sys
from datetime import datetime

def generate_request_id():
    """Generate a unique request ID similar to the ones in the GOR file."""
    # Create a UUID and use part of its hex representation
    return uuid.uuid4().hex[:24]

def get_timestamp():
    """Get current timestamp in nanoseconds."""
    return int(time.time() * 1000000000)

def extract_requests_from_excel(excel_path, output_path, http_column='http请求'):
    """
    Extract HTTP requests from the Excel file and write them to a GOR file.
    
    Args:
        excel_path (str): Path to the Excel file
        output_path (str): Path to the output GOR file
        http_column (str): Name of the column containing HTTP requests (default: 'http请求')
    """
    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Check if the required column exists
        if http_column not in df.columns:
            print(f"Error: Column '{http_column}' not found in the Excel file")
            sys.exit(1)
        
        # Extract the HTTP requests
        http_requests = df[http_column].dropna().astype(str)
        print(f"Found {len(http_requests)} HTTP requests")
        
        # Write to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, request in enumerate(http_requests):
                # Generate a unique request ID
                request_id = generate_request_id()
                
                # Get current timestamp
                timestamp = get_timestamp()
                
                # Write the metadata line
                f.write(f"1 {request_id} {timestamp} 0\n")
                
                # Write the HTTP request
                f.write(f"{request.strip()}\n")
                
                # Add a blank line between requests if it's not the last request
                if i < len(http_requests) - 1:
                    f.write("\n\n🐵🙈🙉\n")
            f.write("\n\n🐵🙈🙉\n")
            
        print(f"Successfully wrote {len(http_requests)} requests to {output_path}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Extract HTTP requests from Excel and convert to GOR format')
    parser.add_argument('--input', '-i', required=True, help='Path to the input Excel file')
    parser.add_argument('--output', '-o', required=True, help='Path to the output GOR file')
    parser.add_argument('--column', '-c', default='http请求', help="Name of the column containing HTTP requests (default: 'http请求')")
    
    args = parser.parse_args()
    
    # Check if the input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        sys.exit(1)
    
    # Extract the requests
    success = extract_requests_from_excel(args.input, args.output, args.column)
    
    if success:
        print("Conversion completed successfully")
    else:
        print("Conversion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
