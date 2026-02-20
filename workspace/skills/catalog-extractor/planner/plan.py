
import argparse
import json
import sys
import time
import datetime
import traceback
from pathlib import Path
from pypdf import PdfReader

# Import neighboring modules
try:
    from utils import slice_pdf_pages, map_catalog_structure, extract_pypdf_text, log_execution
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import slice_pdf_pages, map_catalog_structure, extract_pypdf_text, log_execution

def initialize_job(pdf_path, job_dir, chunk_size=5):
    """
    Initializes a new catalog extraction job.
    1. Creates User-Defined Job Directory (`job_dir`)
    2. Maps Catalog Structure -> `structure.json`
    3. Slices PDFs into `runs/{start}_{end}/{start}_{end}.pdf`
    4. Generates `state.json` tracking all chunks
    """
    pdf_path = Path(pdf_path).resolve()
    job_dir = Path(job_dir).resolve()
    
    # 1. Create Job Directory Structure
    print(f"[*] Initializing Job in: {job_dir}")
    runs_dir = job_dir / "runs"
    
    job_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Map Catalog Structure
    print(f"[*] Analyzing Catalog Structure: {pdf_path}")
    structure = map_catalog_structure(str(pdf_path))
    
    # Save structure.json
    structure_path = job_dir / "structure.json"
    with open(structure_path, "w") as f:
        json.dump(structure, f, indent=2)
    print(f"    [+] Saved structure map to: {structure_path}")

    # 3. Generate State & Slice PDFs
    
    # Load Source PDF Once
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    print(f"[*] Slicing PDFs & Extracting Text into chunks of {chunk_size} pages...")
    
    state = {
        "catalog_source": str(pdf_path),
        "working_dir": str(job_dir),
        "status": "ready",
        "sections": []
    }
    
    total_chunks = 0
    
    for section in structure["sections"]:
        sec_name = section["name"]
        start_page = section["start_page"]
        end_page = section["end_page"]
        
        # Calculate Chunks for this Section
        chunks = []
        for i in range(start_page, end_page + 1, chunk_size):
            chunk_end = min(i + chunk_size - 1, end_page)
            
            # Directory Name: 8_12
            chunk_slug = f"{i}_{chunk_end}"
            
            # Create Chunk Directory: runs/8_12/
            chunk_dir = runs_dir / chunk_slug
            chunk_dir.mkdir(parents=True, exist_ok=True)
            
            # Define PDF Path: runs/8_12/8_12.pdf
            chunk_pdf_name = f"{chunk_slug}.pdf"
            chunk_pdf_path = chunk_dir / chunk_pdf_name
            
            # Slice & Save PDF
            slice_pdf_pages(reader, i, chunk_end, chunk_pdf_path)

            # Define Text MD Path: runs/8_12/extract.md
            text_md_path = chunk_dir / "extract.md"
            
            # Extract Text Context (using chunk PDF)
            # Offset: If chunk starts at page 8 (i=8), small PDF page 1 needs to be labelled "Page 8"
            # Logic: real_page = index(0) + 1 + offset => 8. Offset = 7.
            extract_pypdf_text(str(chunk_pdf_path), str(text_md_path), pages=None, page_offset=(i - 1))
            
            # Add to State
            chunks.append({
                "start": i,
                "end": chunk_end,
                "status": "PENDING",
                "working_dir": str(chunk_dir),   # Absolute path to chunk folder
                "input_file": str(chunk_pdf_path), # Absolute path to sliced PDF
                "text_file": str(text_md_path)    # Absolute path to text context
            })
            total_chunks += 1
            print(f"    [+] Created chunk: {chunk_slug}")
            
        state["sections"].append({
            "name": sec_name,
            "chunks": chunks
        })

    # Save state.json
    state_path = job_dir / "state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
        
    print(f"\n[*] Job Initialized Successfully!")
    print(f"    Total Sections: {len(state['sections'])}")
    print(f"    Total Chunks:   {total_chunks}")
    print(f"    State File:     {state_path}")
    print("\nNext Steps:")
    print(f"Run the executor script pointing to this job directory: {job_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a Catalog Extraction Job")
    parser.add_argument("pdf_path", help="Absolute path to the source catalog PDF")
    parser.add_argument("job_dir", help="Absolute path to the job workspace directory (e.g. /tmp/my_job)")
    parser.add_argument("--chunk-size", type=int, default=5, help="Pages per chunk (default: 5)")
    
    args = parser.parse_args()
    
    start_time = time.time()
    file_name = Path(sys.argv[0]).name
    args_str = " ".join(sys.argv[1:])
    status = "SUCCESS"
    message = "success"
    
    try:
        initialize_job(args.pdf_path, args.job_dir, args.chunk_size)
    except Exception as e:
        status = "FAILURE"
        message = traceback.format_exc()
        print(f"Error initializing job: {e}")
        traceback.print_exc()
    finally:
        duration = time.time() - start_time
        log_execution(args.job_dir, duration, status, message, file_name, args_str)
        if status == "FAILURE":
            sys.exit(1)
