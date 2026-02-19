import json
import os
import argparse
from pathlib import Path

# NOTE: This script is specialized for technical product catalogs (specifically Alpha Wire style).
# It expects an input JSON structure (from Docling metadata.json) and extracts tables.
# CRITICAL: It currently filters for tables with headers like "Part", "SKU", "Conductor".
# Tables not matching these heuristics are dropped. If adapting for other docs, review `is_technical`.

def transform_to_ai_ready(json_input_path, jsonl_output_path, page_offset=0):
    if not os.path.exists(json_input_path):
        print(f"Error: {json_input_path} not found.")
        return

    with open(json_input_path, 'r') as f:
        data = json.load(f)

    # Build a lookup for all items in the document structure
    items = {}
    for key in ['texts', 'tables', 'pictures', 'groups']:
        if key in data:
            for idx, item in enumerate(data[key]):
                # Store by BOTH index-based ref AND the self_ref provided in the JSON
                items[f"#{key}/{idx}"] = item
                items[f"#/{key}/{idx}"] = item
                if 'self_ref' in item:
                    items[item['self_ref']] = item
    
    processed_refs = set()
    output_chunks = []

    def clean_chunk(chunk):
        """Applies column-shift fix and other cleaning heuristics."""
        tech = chunk.get("technical_data", {})
        keys = list(tech.keys())
        values = list(tech.values())
        
        if not keys: return chunk

        last_val = values[-1]
        
        # Heuristic: Last value is the SKU?
        is_shifted = (last_val == chunk["sku"] or last_val in chunk["sku"] or chunk["sku"] in last_val)
        
        # Special case for "5.03" where sku is "5.03" but real part is "5671"
        if not is_shifted and "mm" in keys[-1]:
                # If the last column is "mm" but has a value like "5920" (no decimals), it's suspicious
                if last_val.replace('.','').isdigit() and '.' not in last_val and len(last_val) >= 4:
                    is_shifted = True

        if is_shifted:
            # ROTATE RIGHT
            # New Order: Last Value becomes First. First becomes Second.
            new_values = [values[-1]] + values[:-1]
            
            # Reconstruct Dictionary
            new_tech = {}
            for i, key in enumerate(keys):
                new_tech[key] = new_values[i]
            
            # Update Chunk
            chunk["technical_data"] = new_tech
            
            # Fix SKU if it was weird (like "5.03")
            # The "real" SKU is now in the first position (Part No)
            real_sku = new_values[0]
            chunk["sku"] = real_sku
            
            # Update Content String to reflect changes
            chunk["content"] = f"Product: {chunk['series']}. Category: {chunk['gauge']}. Part Number: {real_sku}. Details: " + \
                                ", ".join([f"{k}: {v}" for k, v in new_tech.items()]) + \
                                f". Page {chunk['page_no']}."
        return chunk

    def process_item(ref, section, gauge):
        if ref in processed_refs:
            return section, gauge
        processed_refs.add(ref)

        item = items.get(ref)
        if not item:
            return section, gauge

        label = item.get('label', '')

        # Update context
        if label in ['section_header', 'header', 'title']:
            text = item.get('text', '').strip()
            if text:
                if 'AWG' in text:
                    gauge = text
                else:
                    section = text
            return section, gauge

        # Handle Tables
        if label == 'table':
            table_data = item.get('data', {})
            grid = table_data.get('grid', [])
            if grid:
                header_texts = []
                data_start_row = 0
                for r_idx, row in enumerate(grid):
                    if any(cell.get('column_header') for cell in row):
                        row_texts = [cell.get('text', '').strip() for cell in row]
                        if not header_texts:
                            header_texts = row_texts
                        else:
                            for c_idx, cell_text in enumerate(row_texts):
                                if c_idx < len(header_texts) and cell_text and cell_text not in header_texts[c_idx]:
                                    header_texts[c_idx] += f" {cell_text}"
                        data_start_row = r_idx + 1
                    else: break
                
                is_technical = any(any(k in h for h in header_texts) for k in ["Part", "SKU", "Conductor"])
                if is_technical:
                    for row_idx in range(data_start_row, len(grid)):
                        row = grid[row_idx]
                        row_values = [cell.get('text', '').strip() for cell in row]
                        specs = {header_texts[i]: row_values[i] for i in range(min(len(header_texts), len(row_values))) if header_texts[i] and row_values[i]}
                        
                        sku = None
                        potential_skus = [v for v in row_values if len(v) >= 4]
                        if potential_skus:
                            for s in potential_skus:
                                if s.startswith('5') or '/' in s or s[0].isalpha():
                                    sku = s
                                    break
                            # REMOVED: Fallback to last column ("Unknown") - prefer None/empty to let AI fix downstream.

                        chunk = {
                            "type": "product_spec", "sku": sku, "series": section, "gauge": gauge,
                            "catalog_family_context": section,
                            "series_context": gauge,
                            "page_no": item.get('prov', [{}])[0].get('page_no') + page_offset,
                            "bbox": item.get('prov', [{}])[0].get('bbox'),
                            "technical_data": specs,
                            "content": f"Product: {section}. Category: {gauge}. Part Number: {sku}. Details: " + 
                                       ", ".join([f"{k}: {v}" for k, v in specs.items() if k.lower() != 'part no']) + 
                                       f". Page {item.get('prov', [{}])[0].get('page_no') + page_offset}."
                        }
                        
                        # Apply Cleaning Immediately
                        chunk = clean_chunk(chunk)
                        output_chunks.append(chunk)
                # Note: Non-technical tables (selection guides) are implicitly dropped by not having an 'else' block here to append them.
                # If we wanted them, we'd add them here, but we explicitly want to filter them out.

        # Recurse into children
        if 'children' in item:
            for child_ref_obj in item['children']:
                c_ref = child_ref_obj.get('$ref')
                if c_ref:
                    section, gauge = process_item(c_ref, section, gauge)
        
        return section, gauge

    # Start recursion from body
    body = data.get('body', {})
    body_children = body.get('children', [])
    
    curr_sec, curr_gauge = "General Catalog", "N/A"
    for ref_obj in body_children:
        ref = ref_obj.get('$ref')
        if ref:
            curr_sec, curr_gauge = process_item(ref, curr_sec, curr_gauge)

    # Sort output chunks by page_no (ascending) then bbox top (ascending)
    def sort_key(chunk):
        page = chunk.get('page_no', 0) or 0
        bbox = chunk.get('bbox')
        
        y_coord = 0
        if isinstance(bbox, list) and len(bbox) >= 2:
            # Assuming Top-Left Origin (Docling v2 JSON): y is top.
            y_coord = bbox[1]
        elif isinstance(bbox, dict):
            y_coord = bbox.get('t', bbox.get('top', bbox.get('y', 0)))
            
        return (page, y_coord)

    if any(c.get('page_no') for c in output_chunks):
        output_chunks.sort(key=sort_key)

    # Write to JSONL
    output_path = Path(jsonl_output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for chunk in output_chunks:
            f.write(json.dumps(chunk) + '\n')

    print(f"SUCCESS: Generated {len(output_chunks)} cleaned product chunks.")
    print(f"File saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform Docling JSON into AI-ready Product Card chunks.")
    parser.add_argument("--input", required=True, help="Path to the input Docling JSON file.")
    parser.add_argument("--output", required=True, help="Path where the output JSONL file will be saved.")
    parser.add_argument("--page-offset", type=int, default=0, help="Offset for page numbering")
    
    args = parser.parse_args()
    
    transform_to_ai_ready(args.input, args.output, args.page_offset)
