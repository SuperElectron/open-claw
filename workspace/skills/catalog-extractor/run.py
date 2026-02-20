
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_pipeline(input_pdf, start_page=1):
    script_dir = Path(__file__).parent.resolve()
    input_pdf = Path(input_pdf).resolve()
    
    # Calculate Page Offset (docling sees page 1, we want page 'start_page')
    page_offset = start_page - 1
    
    # Create Timestamped Output Directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_base = Path("/Users/mat/.openclaw/workspace/generated")
    output_dir = output_base / f"catalog-extractor-{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define Sub-Directories
    raw_dir = output_dir / "raw"
    final_dir = output_dir / "final"

    print(f"=== Starting Catalog Assembly Pipeline ===")
    print(f"Input: {input_pdf}")
    print(f"Start Page: {start_page} (Offset: {page_offset})")
    print(f"Output: {output_dir}")
    print("------------------------------------------")

    # Step 1: Export Assets & Metadata
    print("\n[Step 1] Exporting Assets & Provenance Map...")
    # export_assets.py <pdf_path> <output_dir> --page-offset N
    if not raw_dir.exists(): raw_dir.mkdir(parents=True)
    if not final_dir.exists(): final_dir.mkdir(parents=True)

    cmd1 = [sys.executable, str(script_dir / "export_assets.py"), str(input_pdf), str(raw_dir), "--page-offset", str(page_offset)]
    subprocess.check_call(cmd1)

    # Step 2: Extract Text Context
    print("\n[Step 2] Extracting Raw Text Context...")
    # extract_text_pypdf.py <input_pdf> <output_md> --page-offset N
    text_md = raw_dir / "text_pypdf.md"
    cmd2 = [sys.executable, str(script_dir / "extract_text_pypdf.py"), str(input_pdf), str(text_md), "--page-offset", str(page_offset)]
    subprocess.check_call(cmd2)

    # Step 3: Process & Clean SKUs
    print("\n[Step 3] Processing SKU Data...")
    # skus.py --input ... --output ... --page-offset N
    input_json = raw_dir / "metadata.json"
    output_skus = raw_dir / "sku_intermediate.jsonl" 
    cmd3 = [sys.executable, str(script_dir / "skus.py"), "--input", str(input_json), "--output", str(output_skus), "--page-offset", str(page_offset)]
    subprocess.check_call(cmd3)

    # Step 4: AI Synthesis (Catalog Generation)
    print("\n[Step 4] Synthesizing Final Catalog (AI)...")
    # synthesize.py <export_dir>
    cmd4 = [sys.executable, str(script_dir / "synthesize.py"), str(output_dir)]
    subprocess.check_call(cmd4)

    print("\n==========================================")
    print("Pipeline Complete!")
    print(f"Final Catalog: {final_dir / 'catalog.md'}")
    print(f"Final SKUs:    {final_dir / 'sku.jsonl'}")
    print("==========================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf")
    parser.add_argument("--start-page", type=int, default=1, help="Logical start page number of the input file")
    args = parser.parse_args()

    run_pipeline(args.input_pdf, args.start_page)
