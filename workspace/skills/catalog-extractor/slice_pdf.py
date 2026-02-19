
import sys
from pypdf import PdfReader, PdfWriter

if len(sys.argv) < 5:
    print("Usage: python slice_pdf.py <input> <output> <start_page> <end_page>")
    sys.exit(1)

input_pdf = sys.argv[1]
output_pdf = sys.argv[2]
start_page = int(sys.argv[3])
end_page = int(sys.argv[4])

print(f"Slicing {input_pdf} pages {start_page}-{end_page}...")
reader = PdfReader(input_pdf)
writer = PdfWriter()

# pypdf uses 0-based indexing, user provided 1-based
# pages 12-14 means indices 11, 12, 13
for i in range(start_page - 1, end_page): 
    if i < len(reader.pages):
        writer.add_page(reader.pages[i])

with open(output_pdf, "wb") as f:
    writer.write(f)
print(f"Saved to {output_pdf}")
