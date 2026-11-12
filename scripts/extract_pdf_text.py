#!/usr/bin/env python3
"""
Extract full text from a scientific paper PDF using pdfplumber.
Outputs page-delimited text file for subsequent deep reading.

Usage:
    python extract_pdf_text.py <pdf_path> [output_path]

If output_path is omitted, saves to the same directory as PDF as 'full_text.txt'.
"""

import sys
import os

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)


def extract_pdf(pdf_path: str, output_path: str | None = None) -> str:
    """Extract all text from PDF, page by page."""

    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(pdf_path), "full_text.txt"
        )

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")

        all_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            all_text.append(f"=== PAGE {i + 1} ===\n{text}")
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{total_pages} pages...")

        full_text = "\n\n".join(all_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"Text extracted: {len(full_text)} characters")
    print(f"Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_text.py <pdf_path> [output_path]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    extract_pdf(pdf_path, output_path)
