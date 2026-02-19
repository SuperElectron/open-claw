import logging
import sys
import json
import time
from pathlib import Path

# --- SAFETY PATCH ---
# Fixes "SystemError: tile cannot extend outside image" crash on tiny elements
import PIL.Image
try:
    from docling_core.types.doc.document import ImageRef
    original_from_pil = ImageRef.from_pil

    def safe_from_pil(cls, image, dpi=72):
        if image.width < 1 or image.height < 1:
            logging.warning(f"SAFETY: Blocked crash on 0-area image ({image.width}x{image.height}). Using placeholder.")
            image = PIL.Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return original_from_pil(image=image, dpi=dpi)

    ImageRef.from_pil = classmethod(safe_from_pil)
except Exception as e:
    logging.warning(f"Could not apply safety patch: {e}")
# ---------------------

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if len(sys.argv) < 3:
        print("Usage: python extract_metadata.py <input_pdf> <output_dir>")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    assets_dir = output_dir / "assets"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    logging.info(f"Processing: {input_path}")
    logging.info(f"Output: {output_dir}")

    # Configure Pipeline for Technical Catalogs
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
    pipeline_options.generate_picture_images = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    
    try:
        logging.info("Starting conversion (Standard Pipeline + Accurate Tables)...")
        result = converter.convert(input_path)
        
        # 1. Save Full JSON Structure (Metadata)
        logging.info("Saving metadata.json (Step 2)...")
        # Use export_to_dict to get the raw structure we need for skus.py
        with open(assets_dir / "metadata.json", "w") as f:
            json.dump(result.document.export_to_dict(), f, indent=2)

        # 2. Save Markdown Tables (Step 3)
        logging.info("Saving tables.md (Step 3)...")
        md_text = result.document.export_to_markdown(image_mode="referenced")
        with open(assets_dir / "tables.md", "w") as f:
            f.write(md_text)
            
        runtime = time.time() - start_time
        logging.info(f"SUCCESS! Processed in {runtime:.2f}s")
        
    except Exception as e:
        logging.error(f"Conversion failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
