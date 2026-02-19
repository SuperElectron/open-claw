import sys
from pathlib import Path
from pypdf import PdfReader

def extract_pypdf_text(pdf_path, output_path, pages=None, page_offset=0):
    reader = PdfReader(pdf_path)
    
    with open(output_path, "w") as f:
        f.write(f"# Raw Text Dump (pypdf)\nSource: {pdf_path}\n\n")
        
        # Determine page range (0-indexed)
        if pages:
            start, end = pages
            # Ensure within bounds
            start = max(0, start - 1)  # User input 1-based -> 0-based
            end = min(len(reader.pages), end)
            page_indices = range(start, end)
        else:
            page_indices = range(len(reader.pages))

        for i in page_indices:
            page = reader.pages[i]
            text = page.extract_text()
            
            real_page_num = i + 1 + page_offset
            f.write(f"## Page {real_page_num}\n\n")
            f.write(text)
            f.write("\n\n---\n\n")
            
    print(f"Extracted pypdf text to: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_in")
    parser.add_argument("md_out")
    parser.add_argument("--pages", help="start-end (1-based)")
    parser.add_argument("--page-offset", type=int, default=0, help="Offset for page numbering")
    args = parser.parse_args()
    
    page_range = None
    if args.pages:
        s, e = map(int, args.pages.split("-"))
        page_range = (s, e)

    extract_pypdf_text(args.pdf_in, args.md_out, page_range, args.page_offset)
