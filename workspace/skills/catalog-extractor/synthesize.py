import os
import sys
import json
import re
import time
from pathlib import Path
from dotenv import load_dotenv

# Load Environment Variables from .env file (if present)
load_dotenv()

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# API Setup
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

def synthesize_catalog(export_dir):
    export_path = Path(export_dir).resolve()
    raw_dir = export_path / "raw"
    images_dir = raw_dir / "images"
    final_dir = export_path / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Text Context (pypdf)
    text_map = {}
    text_md_path = raw_dir / "text_pypdf.md"
    if text_md_path.exists():
        content = text_md_path.read_text()
        # Split by "## Page N"
        parts = re.split(r"## Page (\d+)", content)
        for i in range(1, len(parts), 2):
            page_num = int(parts[i])
            page_text = parts[i+1].strip()
            text_map[page_num] = page_text
    else:
        print("Warning: No text_pypdf.md found.")

    # 1b. Load Image Provenance Map
    prov_map = []
    prov_path = raw_dir / "image_provenance_map.json"
    if prov_path.exists():
        try:
            with open(prov_path, 'r') as f:
                prov_map = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load provenance map: {e}")
    else:
        print("Warning: No image_provenance_map.json found.")

    # 1c. Load Intermediate SKU Data (Docling Extraction)
    sku_map = {}
    sku_path = raw_dir / "sku_intermediate.jsonl"
    if sku_path.exists():
        try:
            with open(sku_path, 'r') as f:
                for line in f:
                    try:
                        chunk = json.loads(line)
                        p = chunk.get('page_no', 0)
                        if p not in sku_map: sku_map[p] = []
                        sku_map[p].append(chunk)
                    except: pass
        except Exception as e:
            print(f"Warning: Could not load SKU intermediate data: {e}")

    # 2. Iterate Images (Pages)
    image_files = sorted(
        list(images_dir.glob("page*.png")),
        key=lambda x: int(x.stem.replace("page", ""))
    )
    
    sku_output_path = final_dir / "sku.jsonl"
    catalog_output_path = final_dir / "catalog.md"
    
    # Clear outputs
    with open(sku_output_path, "w") as f: pass
    with open(catalog_output_path, "w") as f: 
        f.write("# Product Catalog (Synthesized)\n\n")

    # Model Setup
    model_name = 'gemini-2.0-flash'
    model = genai.GenerativeModel(model_name)
    
    print(f"Synthesizing {len(image_files)} pages using {model_name}...")

    # Token Tracking
    token_stats = {
        "model": model_name,
        "total_input": 0,
        "total_output": 0,
        "pages_processed": 0
    }

    for img_path in image_files:
        # Extract page number from filename "page9.png"
        try:
            page_num = int(img_path.stem.replace("page", ""))
        except ValueError:
            continue
            
        print(f"Processing Page {page_num}...")
        
        # Get Context
        raw_text = text_map.get(page_num, "")
        
        # Filter Provenance for Current Page
        page_prov = [item for item in prov_map if item.get('page_number') == page_num]
        prov_json_str = json.dumps(page_prov, indent=2)

        # Filter SKU Context for Current Page
        page_skus = sku_map.get(page_num, [])
        # Format for AI as concise text
        sku_context_str = json.dumps([
            {
                "sku": s.get("sku"),
                "desc": s.get("content"),
                "bbox": s.get("bbox")
            } for s in page_skus
        ], indent=2)

        # Prompt
        # NEW: Visual Gap Analysis & Content Restoration
        prompt = f"""
        You are a highly accurate Catalog Digitization Agent.
        Your goal is to convert this product catalog page (Image + Raw Text + Structured Data) into two outputs:
        1. A clean Markdown document section.
        2. A structured JSON dataset of Product SKUs.

        INPUTS:
        - Image: The visual ground truth.
        - Text: "{raw_text[:2000]}..." (OCR/Extraction - may have noise).
        - Image Provenance (Available Crops/Diagrams):
        ```json
        {prov_json_str}
        ```
        - Structured Data (Pre-extracted Context):
        ```json
        {sku_context_str}
        ```

        INSTRUCTIONS:
        
        TASK 1: CATALOG MARKDOWN
        - Reconstruct the page content in Markdown.
        - Use correct headers (#, ##, ###) based on the visual hierarchy.
        - Fix any broken text from the raw stream (e.g. join "Indus-" "trial").
        - Insert the image `![Page {page_num}](raw/images/{img_path.name})` at the top.
        - **Visual Gap Analysis & Content Restoration:**
            1.  **Analyze the Page Image:** Identify all visually significant elements such as **large diagrams**, **technical tables**, **section headers**, and **icons**. Use the provided bounding box (`bbox`) coordinates in the `image_provenance_map.json` to determine importance (e.g., larger area = higher significance).
            2.  **Cross-Reference with Extracted Data:** Compare these visual elements against the provided JSONL text/table data for the corresponding page.
            3.  **Detect Missing Information:** If a significant visual element (e.g., a wiring diagram or a specific technical table) is present in the image but **missing** or poorly represented in the text extraction:
                *   **Explicitly include it** in the Markdown output.
                *   Use the `image_provenance_map.json` to find the correct image filename for that element.
                *   Insert the image with a descriptive caption derived from its context (e.g., "Figure: Shielding Configuration").
            4.  **Preserve Structure:** Ensure all section headers and anchors visible in the image are reflected in the Markdown structure to maintain the document's logical flow.
        - Format tables as clean Markdown tables.

        TASK 2: SKU EXTRACTION
        - Identify any Product Specification Tables.
        - Extract EVERY row into a JSON object.
        - Fields:
          - `sku`: The Part Number (e.g., "5920", "5020/15C").
          - `series`: The Product Series (e.g., "Xtra-Guard 1") found in the page header.
          - `description`: Brief description or category (e.g., "High Performance PVC").
          - `specs`: A dictionary of all technical columns (Conductors, Diameter, Gauge, etc.).
          - `provenance`: {{ "page": {page_num}, "file": "catalog.pdf" }}
        
        OUTPUT FORMAT (JSON):
        Return a single JSON object with this structure:
        {{
            "markdown_content": "The markdown string...",
            "skus": [ {{...sku_object...}}, ... ]
        }}
        """

        # Call API
        # Load Image (Inline)
        import PIL.Image
        img = PIL.Image.open(img_path)
        
        response = model.generate_content(
            [prompt, img],
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Track Tokens
        if response.usage_metadata:
            in_tok = response.usage_metadata.prompt_token_count
            out_tok = response.usage_metadata.candidates_token_count
            token_stats["total_input"] += in_tok
            token_stats["total_output"] += out_tok
            token_stats["pages_processed"] += 1
            print(f"  -> Tokens: {in_tok} In / {out_tok} Out")
        
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"  !! JSON Parse Error on Page {page_num}: {e}")
            print(f"  !! Raw Response Snippet: {response.text[:500]}...")
            # Critical Error: Exit immediately
            sys.exit(1)
        
        # Save Results
        markdown = result.get("markdown_content", "")
        skus = result.get("skus", [])
        
        # Append Markdown
        with open(catalog_output_path, "a") as f:
            f.write(markdown + "\n\n---\n\n")
        
        # Append SKUs
        with open(sku_output_path, "a") as f:
            for sku in skus:
                f.write(json.dumps(sku) + "\n")
        
        print(f"  -> Extracted {len(skus)} SKUs.")

    # Save Token Stats
    stats_path = final_dir / "token_usage.json"
    with open(stats_path, "w") as f:
        json.dump(token_stats, f, indent=2)

    print("\n=== TOKEN USAGE SUMMARY ===")
    print(f"Pages: {token_stats['pages_processed']}")
    print(f"Input: {token_stats['total_input']:,}")
    print(f"Output: {token_stats['total_output']:,}")
    print(f"Total: {token_stats['total_input'] + token_stats['total_output']:,}")
    print("===========================")
    print(f"Done. Outputs in {final_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python synthesize.py <export_dir>")
        sys.exit(1)
        
    synthesize_catalog(sys.argv[1])
