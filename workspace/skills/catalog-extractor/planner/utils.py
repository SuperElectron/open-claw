
from pathlib import Path
from pypdf import PdfWriter
import json
import datetime

def log_execution(job_dir, duration, status, message, file_name, args_str):
    if not job_dir: return
    try:
        minutes = int(duration // 60)
        seconds = duration % 60
        time_str = f"{minutes}m {seconds:.3f}s"
        
        msg_log = message.replace('\n', '\\n').replace('\r', '') if message != 'success' else 'success'
        dt_str = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
        log_line = f"[{dt_str}] {file_name} {args_str} | time=\"{time_str}\" status=\"{status}:{msg_log}\"\n"
        
        jdir = Path(job_dir)
        jdir.mkdir(parents=True, exist_ok=True)
        
        with open(jdir / "execution.log", "a") as f:
            f.write(log_line)
            
        state_file = jdir / "state.json"
        state = {}
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    state = json.load(f)
            except Exception:
                pass
                
        if "executions" not in state:
            state["executions"] = []
            
        state["executions"].append({
            "datetime": dt_str,
            "file": file_name,
            "args": args_str,
            "execution_time": time_str,
            "status": status,
            "message": message
        })
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Failed to log execution: {e}")



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

def slice_pdf_pages(reader, start_page: int, end_page: int, output_path: Path):
    """
    Slices pages `start_page` to `end_page` (inclusive, 1-based) from `reader`
    and saves them to `output_path`.
    """
    writer = PdfWriter()
    total_pages = len(reader.pages)
    
    # Iterate through the range, converting 1-based page numbers to 0-based indices
    for p in range(start_page - 1, end_page):
        if 0 <= p < total_pages:
            writer.add_page(reader.pages[p])
            
    with open(output_path, "wb") as f:
        writer.write(f)

import re
from pypdf import PdfReader

def map_catalog_structure(pdf_path) -> dict:
    """
    Scans the PDF TOC to identify logical sections.
    Returns the structure dict.
    """
    reader = PdfReader(pdf_path)
    
    # TOC is usually on pages 2-3 (indices 1-2)
    # We'll scan a bit wider just in case: 1-5 (indices 0-4)
    toc_text = ""
    for i in range(0, min(5, len(reader.pages))):
        try:
            text = reader.pages[i].extract_text()
            if text:
                toc_text += text + "\n"
        except:
            pass

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
    
    if not sections:
        print("Warning: No sections found in TOC. Creating a single 'Full Catalog' section.")
        sections.append({
            "name": "Full Catalog",
            "start_page": 1,
            "end_page": len(reader.pages)
        })
        return {
            "source": str(pdf_path),
            "total_pages": len(reader.pages),
            "sections": sections
        }

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
    
    return structure
