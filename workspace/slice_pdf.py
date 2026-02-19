
import sys
from pypdf import PdfReader, PdfWriter

def extract_pages(input_path, output_path, start_page, end_page):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # PDF pages are 0-indexed
    # User provided 1-indexed pages (23-27 inclusive)
    # So we want indices 22 to 26
    start_idx = start_page - 1
    end_idx = end_page  # slice is exclusive at the end, so 27 is correct for page 27 (index 26)
    
    # Add pages
    for i in range(start_idx, end_idx):
        if i < len(reader.pages):
            writer.add_page(reader.pages[i])
            
    with open(output_path, "wb") as f:
        writer.write(f)

if __name__ == "__main__":
    extract_pages(
        "/Users/mat/code/paykali/open-claw/infra/mcp/_data/catalog.pdf",
        "generated/chunks/section1_chunk_23_27.pdf",
        23,
        27
    )
