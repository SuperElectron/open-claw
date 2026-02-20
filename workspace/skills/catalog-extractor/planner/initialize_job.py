
import argparse
import json
import logging
import sys
from pathlib import Path
from math import ceil

# Import the map_catalog function from the neighboring file
try:
    from map_catalog import map_catalog_structure
except ImportError:
    # If running directly from script, add local dir to path
    import sys
    sys.path.append(str(Path(__file__).parent))
    from map_catalog import map_catalog_structure

def initialize_job(pdf_path, working_dir, chunk_size=5):
    """
    Initializes a new catalog extraction job.
    1. Creates Workspace
    2. Maps Catalog Structure
    3. Generates Extraction State JSON with Chunks
    """
    pdf_path = Path(pdf_path).resolve()
    working_dir = Path(working_dir).resolve()
    
    # 1. Create Workspace Structure
    print(f"[*] Initializing Job in: {working_dir}")
    chunks_dir = working_dir / "chunks"
    runs_dir = working_dir / "runs"
    
    working_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Map Catalog Structure
    print(f"[*] Analyzing Catalog Structure: {pdf_path}")
    structure = map_catalog_structure(str(pdf_path))
    
    # Save Structure JSON
    structure_path = working_dir / "catalog_structure.json"
    with open(structure_path, "w") as f:
        json.dump(structure, f, indent=2)
    print(f"    [+] Saved structure map to: {structure_path}")

    # 3. Generate Extraction State
    state = {
        "catalog_source": str(pdf_path),
        "working_dir": str(working_dir),
        "status": "ready",
        "sections": []
    }
    
    total_chunks = 0
    
    for section in structure["sections"]:
        sec_name = section["name"]
        start_page = section["start_page"]
        end_page = section["end_page"]
        
        # Calculate Chunks
        chunks = []
        for i in range(start_page, end_page + 1, chunk_size):
            chunk_end = min(i + chunk_size - 1, end_page)
            
            # Sub-range: i to chunk_end
            chunk_slug = f"page_{i}_{chunk_end}"
            chunk_filename = f"chunk_{i}_{chunk_end}.pdf"
            chunk_output_path = chunks_dir / chunk_filename
            
            # The run directory where artifacts will be saved
            run_output_dir = runs_dir / f"run_{chunk_slug}"
            
            chunks.append({
                "start": i,
                "end": chunk_end,
                "status": "PENDING",
                "output_dir": str(run_output_dir), # Absolute path
                "input_file": str(chunk_output_path) # Absolute path (to be created by slice_pdf later)
            })
            total_chunks += 1
            
        state["sections"].append({
            "name": sec_name,
            "chunks": chunks
        })

    # Save State JSON
    state_path = working_dir / "extraction_state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)
        
    print(f"[*] Job Initialized Successfully!")
    print(f"    Total Sections: {len(state['sections'])}")
    print(f"    Total Chunks:   {total_chunks}")
    print(f"    State File:     {state_path}")
    print("\nNext Steps:")
    print("1. Slice the PDF into chunks based on the state file.")
    print("2. Run the extraction pipeline on each chunk.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a Catalog Extraction Job")
    parser.add_argument("--pdf-path", required=True, help="Absolute path to the source catalog PDF")
    parser.add_argument("--working-dir", required=True, help="Absolute path to the job workspace directory")
    parser.add_argument("--chunk-size", type=int, default=5, help="Pages per chunk (default: 5)")
    
    args = parser.parse_args()
    
    try:
        initialize_job(args.pdf_path, args.working_dir, args.chunk_size)
    except Exception as e:
        print(f"Error initializing job: {e}")
        sys.exit(1)
