
import sys
import json
import time
import datetime
import traceback
import argparse
from pathlib import Path

# Add the current directory to sys.path so we can import from 'extract'
sys.path.append(str(Path(__file__).parent))

try:
    from extract.export_assets import export_assets
    from extract.skus import process_skus
    from extract.synthesize import synthesize_catalog
    from planner.utils import log_execution
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Ensure you are running this from the skills/catalog-extractor directory.")
    sys.exit(1)

def load_state(job_dir):
    state_path = Path(job_dir) / "state.json"
    if not state_path.exists():
        print(f"Error: state.json not found in {job_dir}")
        return None
    with open(state_path, "r") as f:
        return json.load(f)

def save_state(job_dir, state):
    state_path = Path(job_dir) / "state.json"
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

def print_report(state):
    print("\n=== Job State Report ===")
    sections = state.get("sections", [])
    if not sections:
        print("No sections found in state.")
        return
        
    for i, section in enumerate(sections):
        title = section.get("title", f"Section {i}")
        status_counts = {}
        chunks = section.get("chunks", [])
        
        for chunk in chunks:
            status = chunk.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            
        # Format the counts summary
        counts_str = ", ".join([f"{status}: {count}" for status, count in status_counts.items()])
        if not counts_str:
            counts_str = "No chunks"
            
        print(f"{i}: {title} - {counts_str}")
    print("========================\n")

def find_next_chunk(state, synthesis_mode, target_section_idx=None):
    """Finds the next chunk to process based on synthesis_mode and optional section index."""
    sections = state.get("sections", [])
    
    # Priority 1: If include or skip, look for PENDING
    if synthesis_mode in ["include", "skip"]:
        for i, section in enumerate(sections):
            if target_section_idx is not None and i != target_section_idx:
                continue
            for chunk in section.get("chunks", []):
                if chunk.get("status") == "PENDING":
                    return chunk

    # Priority 2: If include or only, look for SYNTHESIZE
    if synthesis_mode in ["include", "only"]:
        for i, section in enumerate(sections):
            if target_section_idx is not None and i != target_section_idx:
                continue
            for chunk in section.get("chunks", []):
                if chunk.get("status") == "SYNTHESIZE":
                    return chunk

    return None

def process_chunk(chunk, job_dir, original_status, synthesis_mode):
    """Executes the extraction pipeline for a single chunk."""
    
    # Paths from State
    chunk_dir = Path(chunk["working_dir"])
    input_pdf = Path(chunk["input_file"])
    
    # Ensure they exist (relative to job_dir if absolute paths fail, but state has absolute)
    if not input_pdf.exists():
        print(f"CRITICAL: Input PDF not found at {input_pdf}")
        return "FAILED"

    print(f"\n=== Processing Chunk: {chunk['start']}-{chunk['end']} ===")
    print(f"Working Dir: {chunk_dir}")
    print(f"Original Status: {original_status} | Mode: {synthesis_mode}")
    
    start_time = time.time()
    
    try:
        if original_status == "PENDING":
            # Step 1: Docling Export (Heavy Lift)
            # Arguments: pdf_path, output_dir, page_offset
            # Offset calculation: 
            #   Chunk Start: 8. 
            #   Chunk PDF Page 1 -> Real Page 8.
            #   Offset = 8 - 1 = 7.
            page_offset = chunk["start"] - 1
            
            print(f"[1/3] Running Docling Export (Offset: {page_offset})...")
            export_assets(str(input_pdf), str(chunk_dir), page_offset=page_offset)

            # Step 2: SKU Processing
            print(f"[2/3] Processing SKU Data...")
            metadata_json = chunk_dir / "metadata.json"
            sku_output = chunk_dir / "sku_intermediate.jsonl"
            process_skus(str(metadata_json), str(sku_output), page_offset=page_offset)

            if synthesis_mode == "skip":
                duration = time.time() - start_time
                print(f"=== Chunk Extraction Complete in {duration:.1f}s (Synthesis Skipped) ===")
                return "SYNTHESIZE"

        # Step 3: Synthesis
        print(f"[3/3] Synthesizing Final Output...")
        synthesize_catalog(str(chunk_dir))
        
        duration = time.time() - start_time
        print(f"=== Chunk Complete in {duration:.1f}s ===")
        return "COMPLETED"

    except Exception as e:
        print(f"!!! Error processing chunk: {e}")
        import traceback
        traceback.print_exc()
        return "FAILED"

def run_job(job_dir, run_once=False, synthesis_mode="include", target_section_idx=None):
    """Main loop to pick up pending jobs."""
    job_dir = Path(job_dir).resolve()
    print(f"[*] Starting Runner for Job: {job_dir}")
    print(f"[*] Synthesis Mode: {synthesis_mode}")
    if target_section_idx is not None:
        print(f"[*] Target Section: {target_section_idx}")
    
    while True:
        # 1. Load State
        state = load_state(job_dir)
        if not state: break
        
        # 2. Find Work
        chunk = find_next_chunk(state, synthesis_mode, target_section_idx)
        
        if not chunk:
            print("[*] No chunks found matching criteria. Job Complete!")
            break
            
        # 3. Mark IN_PROGRESS
        original_status = chunk.get("status", "PENDING")
        print(f"[*] Claiming Chunk {chunk['start']}-{chunk['end']} (Status: {original_status})...")
        chunk["status"] = "IN_PROGRESS"
        save_state(job_dir, state)
        
        # 4. Execute
        new_status = process_chunk(chunk, job_dir, original_status, synthesis_mode)
        
        # 5. Update Status
        # Reload state to avoid overwriting concurrent changes (if any)
        state = load_state(job_dir)
        # Find the chunk again to update it
        # (This is a simple linear search re-match)
        target_chunk = None
        for s in state["sections"]:
            for c in s["chunks"]:
                if c["start"] == chunk["start"] and c["end"] == chunk["end"]:
                    target_chunk = c
                    break
            if target_chunk: break
            
        if target_chunk:
            target_chunk["status"] = new_status
            save_state(job_dir, state)
            
        if run_once:
            print("[*] Single run mode complete.")
            break



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Catalog Extractor Runner")
    parser.add_argument("job_dir", help="Path to the initialized job directory")
    parser.add_argument("--once", action="store_true", help="Process only one chunk and exit")
    parser.add_argument("--synthesis", type=str, choices=["skip", "only", "include"], default="include", help="Synthesis mode: skip, only, or include (default)")
    parser.add_argument("--report", action="store_true", help="Print a summary report of the state and exit")
    parser.add_argument("--section", type=int, help="Only process chunks within this specific section index (e.g., 0)")
    
    args = parser.parse_args()
    
    start_time = time.time()
    file_name = Path(sys.argv[0]).name
    args_str = " ".join(sys.argv[1:])
    status = "SUCCESS"
    message = "success"
    
    try:
        if args.report:
            state = load_state(args.job_dir)
            if state:
                print_report(state)
            else:
                print(f"Could not load state from {args.job_dir}")
        else:
            run_job(args.job_dir, run_once=args.once, synthesis_mode=args.synthesis, target_section_idx=args.section)
    except Exception as e:
        status = "FAILURE"
        message = traceback.format_exc()
        print(f"Error during execution: {e}")
        traceback.print_exc()
    finally:
        duration = time.time() - start_time
        log_execution(args.job_dir, duration, status, message, file_name, args_str)
        if status == "FAILURE":
            sys.exit(1)
