import logging
import sys
import json
import time
from pathlib import Path

# --- SAFETY PATCH ---
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
        print("Usage: python extract_ingredients.py <input_pdf> <output_dir> [--pages start-end]")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    output_base = Path(sys.argv[2]).resolve()
    
    # Parse Page Range
    page_range = None
    if "--pages" in sys.argv:
        try:
            idx = sys.argv.index("--pages")
            val = sys.argv[idx + 1]
            start, end = map(int, val.split("-"))
            page_range = (start, end)
            logging.info(f"Processing range: Pages {start} to {end}")
        except Exception:
            logging.warning("Invalid page range format. Using full document.")

    # Define "Raw Ingredients" Structure
    raw_dir = output_base / "raw"
    images_dir = raw_dir / "images"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    logging.info(f"Processing: {input_path}")
    logging.info(f"Ingredients Store: {raw_dir}")

    # Configure Pipeline
    # Strategy: 
    # 1. generate_page_images=True -> Visual Ground Truth (Step 1).
    # 2. generate_picture_images=True -> Diagrams/Crops.
    # Note: Text and Tables are handled by other means (pypdf / VLM synthesis).
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False 
    pipeline_options.do_table_structure = False # Disable bad table extraction
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.images_scale = 2.0  # High Res for AI

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    
    try:
        logging.info("Starting conversion (Images Only)...")
        # Apply page range if specified. Default is full doc.
        convert_kwargs = {}
        if page_range:
            convert_kwargs["page_range"] = page_range

        result = converter.convert(input_path, **convert_kwargs)
        doc = result.document
        
        # --- Images (Visual Ground Truth) ---
        logging.info(f"Exporting Page Images to {images_dir}...")
        for page_no, page in doc.pages.items():
            if page.image:
                page_path = images_dir / f"page{page_no}.png"
                page.image.pil_image.save(page_path)
        
        # Save Crops (Pictures)
        logging.info(f"Exporting Diagram Crops...")
        count_crops = 0
        for item, _ in doc.iterate_items():
            if item.label == "picture" and hasattr(item, "image") and item.image:
                page_no = item.prov[0].page_no if item.prov else "unknown"
                # Use ref ID for uniqueness
                ref_id = item.self_ref.split("/")[-1] 
                crop_name = f"crop_p{page_no}_{ref_id}.png"
                item.image.pil_image.save(images_dir / crop_name)
                count_crops += 1
        logging.info(f"-> Saved {len(doc.pages)} pages and {count_crops} crops.")

        runtime = time.time() - start_time
        logging.info(f"SUCCESS! Images extracted in {runtime:.2f}s")
        
    except Exception as e:
        logging.error(f"Extraction failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
