
import sys
import json
import re
from pathlib import Path
from pypdf import PdfReader

def map_catalog_structure(pdf_path, output_path):
    reader = PdfReader(pdf_path)
    
    # TOC is usually on pages 2-3 (indices 1-2)
    # We'll scan a bit wider just in case: 1-5 (indices 0-4)
    toc_text = ""
    for i in range(0, min(5, len(reader.pages))):
        toc_text += reader.pages[i].extract_text() + "\n"

    # Regex to find "Section Name ... PageNumber"
    # Matches lines like: "Xtra-Guard Performance Cable      8"
    # Matches lines like: "EcoGen Cable ................. 109"
    # Capture Group 1: Name, Group 2: Page
    pattern = re.compile(r"^(.+?)(?:\.{2,}|\s{2,})(\d+)$", re.MULTILINE)
    
    matches = pattern.findall(toc_text)
    
    sections = []
    seen_pages = set()

    for name, page_str in matches:
        name = name.strip()
        page = int(page_str)
        
        # Filter noise (page numbers that are too small to be sections, or duplicates)
        if page < 5: continue 
        if page in seen_pages: continue
        
        # Heuristic: Section names shouldn't be too long or look like sentences
        if len(name) > 100: continue
        
        sections.append({
            "name": name,
            "start_page": page,
            # end_page will be calculated later
        })
        seen_pages.add(page)

    # Sort by start page
    sections.sort(key=lambda x: x["start_page"])

    # Calculate end_page (it's the start of the next section - 1)
    # The last section goes to the end of the document (roughly)
    total_pages = len(reader.pages)
    
    for i in range(len(sections)):
        if i < len(sections) - 1:
            sections[i]["end_page"] = sections[i+1]["start_page"] - 1
        else:
            sections[i]["end_page"] = total_pages

    # Structure the output
    structure = {
        "source": str(pdf_path),
        "total_pages": total_pages,
        "sections": sections
    }

    # Save to JSON
    with open(output_path, "w") as f:
        json.dump(structure, f, indent=2)
        
    print(f"Catalog map saved to: {output_path}")
    print(f"Found {len(sections)} sections.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python map_catalog.py <input_pdf> <output_json>")
        sys.exit(1)
        
    map_catalog_structure(sys.argv[1], sys.argv[2])
