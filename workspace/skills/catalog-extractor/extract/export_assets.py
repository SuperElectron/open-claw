
import logging
import json
import os
import sys
from pathlib import Path

# DEBUG: confirm execution
with open('/tmp/debug_doc_extract.txt', 'a') as f:
    f.write(f"Script started at {sys.argv} \n")

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import ImageRefMode

# Setup logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def export_assets(pdf_path: str, output_base_dir: str, page_offset: int = 0):
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_base_dir).resolve()
    image_dir = output_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Processing: {pdf_path}")
    print(f"[*] Output directory: {output_dir}")
    print(f"[*] Page Offset: {page_offset}")
    sys.stdout.flush()
    
    # Configure Pipeline for High-Fidelity Extraction
    options = PdfPipelineOptions()
    options.generate_picture_images = True
    options.generate_page_images = True
    options.images_scale = 2.0  # 2x scale for high quality

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options)
        }
    )

    print("[*] Starting conversion (this may take a moment)...")
    sys.stdout.flush()
    result = converter.convert(pdf_path)
    doc = result.document

    # 1. Save Page Images as pageX.png
    print(f"[*] Saving full-page images for {len(doc.pages)} pages...")
    sys.stdout.flush()
    for page_no, page in doc.pages.items():
        if page.image:
            real_page_no = page_no + page_offset
            page_filename = f"page{real_page_no}.png"
            target_path = image_dir / page_filename
            page.image.pil_image.save(target_path)
            print(f"    [+] Saved: {page_filename}")
            sys.stdout.flush()
        else:
            print(f"    [!] Page {page_no} has no image data.")
            sys.stdout.flush()

    image_mapping = []
    
    # 2. Extract specific picture elements and building provenance map
    print("[*] Extracting specific picture elements...")
    sys.stdout.flush()
    for item, _level in doc.iterate_items():
        if item.label == "picture":
            # Extract basic provenance
            prov = item.prov[0] if item.prov else None
            page_no = prov.page_no if prov else "unknown"
            
            real_page_no = page_no + page_offset if isinstance(page_no, int) else page_no
            
            bbox = prov.bbox.as_tuple() if prov else None
            pic_id = item.self_ref.split('/')[-1] if hasattr(item, 'self_ref') else f"p{real_page_no}_idx{_level}"
            
            # Generate a clean filename for cropping
            filename = f"crop_page_{real_page_no}_{pic_id}.png"
            target_path = image_dir / filename
            
            # Attempt to save the image if it exists in the item
            if hasattr(item, 'image') and item.image:
                item.image.pil_image.save(target_path)
                
                # Capture context: text associated with or near the picture
                context_text = item.text if hasattr(item, 'text') and item.text else ""
                
                image_mapping.append({
                    "filename": filename,
                    "page_number": real_page_no,
                    "bbox": bbox,
                    "label": item.label,
                    "self_ref": item.self_ref,
                    "text_context": context_text,
                    "path": str(target_path.relative_to(output_dir))
                })
                print(f"    [+] Saved crop: {filename} (bbox: {bbox})")
                sys.stdout.flush()
            else:
                print(f"    [!] Picture at page {page_no} has no image data.")
                sys.stdout.flush()

    # 3. Save the Image Provenance Map (JSON)
    map_json_path = output_dir / "image_provenance_map.json"
    print(f"[*] Writing provenance map to: {map_json_path}")
    sys.stdout.flush()
    with open(map_json_path, "w") as f:
        json.dump(image_mapping, f, indent=2)
    
    # 4. Save the Document Overview (Markdown) with Image References
    map_md_path = output_dir / "image_provenance_map.md"
    print(f"[*] Writing human-readable map to: {map_md_path}")
    sys.stdout.flush()
    with open(map_md_path, "w") as f:
        f.write("# Image Provenance Map\n\n")
        f.write(f"Source Document: {pdf_path.name}\n\n")
        f.write("| Image | Page | Context/Caption | Coordinates |\n")
        f.write("| :--- | :---: | :--- | :--- |\n")
        for entry in image_mapping:
            bbox_str = str(entry.get('bbox', 'N/A'))
            f.write(f"| ![]({entry['path']}) | {entry['page_number']} | {entry['text_context']} | {bbox_str} |\n")

    # 5. Save Full Document JSON for SKU Processor
    json_path = output_dir / "metadata.json"
    print(f"[*] Saving full document JSON to: {json_path}")
    sys.stdout.flush()
    doc.save_as_json(json_path)

    print("[*] Done.")
    sys.stdout.flush()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path", help="Path to PDF")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--page-offset", type=int, default=0, help="Offset to add to page numbers")
    args = parser.parse_args()
    
    export_assets(args.pdf_path, args.output_dir, args.page_offset)
