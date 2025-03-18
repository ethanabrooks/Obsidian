#!/usr/bin/env python3
"""
A simple CLI tool to convert CSV files to Markdown tables.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import TextIO


def csv_to_markdown(csv_file: TextIO, output_file: TextIO) -> None:
    """
    Convert CSV content to Markdown table format.
    
    Args:
        csv_file: Input file object containing CSV data
        output_file: Output file object where markdown will be written
    """
    reader = csv.reader(csv_file)
    
    # Read header row
    try:
        headers = next(reader)
    except StopIteration:
        print("Error: Empty CSV file", file=sys.stderr)
        return
    
    # Write header row
    output_file.write("| " + " | ".join(headers) + " |\n")
    
    # Write separator row
    output_file.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
    
    # Write data rows
    for row in reader:
        # Escape pipe characters in the data
        escaped_row = [cell.replace("|", "\\|") for cell in row]
        output_file.write("| " + " | ".join(escaped_row) + " |\n")


def main() -> None:
    """Parse arguments and convert CSV to Markdown."""
    parser = argparse.ArgumentParser(description="Convert CSV files to Markdown tables")
    parser.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin,
                        help="Input CSV file (default: stdin)")
    parser.add_argument("-o", "--output", type=argparse.FileType("w"), default=sys.stdout,
                        help="Output Markdown file (default: stdout)")
    
    args = parser.parse_args()
    
    try:
        csv_to_markdown(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.input is not sys.stdin:
            args.input.close()
        if args.output is not sys.stdout:
            args.output.close()


if __name__ == "__main__":
    main() 