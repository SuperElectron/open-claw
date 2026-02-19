---
name: catalog-extractor
description: Extract high-fidelity product data from PDF catalogs using visual analysis (Docling) and AI synthesis (Gemini).
metadata:
  openclaw:
    emoji: "📑"
    requires:
      bins: ["uv"]
    install:
      - id: "deps"
        kind: "exec"
        command: "uv venv ~/.cache/openclaw-catalog-env && uv pip install docling pypdf google-generativeai python-dotenv --python ~/.cache/openclaw-catalog-env/bin/python"
        label: "Install Python dependencies (Global Cache)"
---

# Catalog Extraction Skill

This skill extracts high-fidelity product data from PDF catalogs, combining visual analysis with structured text extraction.

## Workflow

The extraction process follows a strict 4-step pipeline:

### 1. Asset Generation (`export_assets.py`)
- **Action:** Generates high-resolution page images (2x scale) and micro-crops of all picture elements.
- **Output:** `raw/images/pageN.png`, `raw/images/crop_*.png`
- **Critical Output:** `raw/image_provenance_map.json`
    - Contains filenames, page numbers, and **bounding box [x,y,w,h]** coordinates.
    - Used by the AI model in Step 4 for "Visual Gap Analysis" (detecting missing diagrams).

### 2. Context Extraction (`extract_text_pypdf.py`)
- **Action:** Extracts raw text from the PDF to provide context for the AI model.
- **Output:** `raw/text_pypdf.md`

### 3. SKU Processing (`skus.py`)
- **Action:** Cleans and structures product data from the Docling JSON.
- **Enrichment:** Adds mandatory `catalog_family_context` and `series_context` to every SKU entry.
- **Sorting:** Sorts chunks by Page Number (ascending) and Vertical Position (top-to-bottom).
- **Output:** `final/sku.jsonl` (Intermediate clean data)

### 4. AI Synthesis (`synthesize.py`)
- **Action:** Generates the final `catalog.md` using a multimodal LLM (Gemini 2.0 Flash).
- **Inputs:** Page Image + Raw Text + **Provenance Map**.
- **Logic:**
    - Reconstructs the page in Markdown.
    - Performs **Visual Gap Analysis**: Uses the `bbox` data from the provenance map to identify significant diagrams missing from the text.
    - Explicitly inserts these missing diagrams with context-aware captions.
    - Extracts structured SKU data into a final JSONL dataset.
- **Output:** `final/catalog.md`, `final/sku.jsonl` (Final)

## Usage

**CRITICAL:** Do NOT run `uv run` locally. Use the cached virtual environment to avoid indexing issues.

Run the pipeline using the explicit Python interpreter:

```bash
~/.cache/openclaw-catalog-env/bin/python assemble_catalog.py <input_pdf>
```

Output location:
`workspace/generated/catalog-extractor-{timestamp}`

Example:
```bash
~/.cache/openclaw-catalog-env/bin/python assemble_catalog.py ../../data/catalog.pdf
```
