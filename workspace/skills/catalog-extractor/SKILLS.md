---
name: catalog-extractor
description: Extract high-fidelity product data from PDF catalogs using visual analysis (Docling) and AI synthesis (Gemini).
metadata:
  openclaw:
    emoji: "📑"
    requires:
      bins: ["uv"],
      env: ["UV_PROJECT_ENVIRONMENT"]
    install:
      - id: "deps"
        kind: "exec"
        command: "UV_PROJECT_ENVIRONMENT=$UV_PROJECT_ENVIRONMENT uv sync"
        label: "Install Python dependencies (workspace Cache)"
---

# Catalog Extraction Skill

This skill extracts high-fidelity product data from PDF catalogs, combining visual analysis with structured text extraction.

## Workflow

The extraction process follows a strict 4-step pipeline:

### 1. Asset Generation (`export_assets.py`)
- **Arguments:** 
  - `pdf_path`: Input PDF file path.
  - `output_dir`: Output directory for assets.
  - `--page-offset <N>`: Page offset for naming assets.
- **Outputs:** 
  - `raw/images/pageN.png`: High-resolution page images (2x scale).
  - `raw/images/crop_*.png`: Micro-crops of picture elements.
  - `raw/image_provenance_map.json`: Critical map containing filenames, real page numbers, and bounding box [x,y,w,h] coordinates.
  - `raw/metadata.json`: Full Docling extraction data.
- **Action:** Generates visual assets and strictly names them based on the provided page offset to maintain provenance. Compiles a provenance map used for downstream "Visual Gap Analysis".

### 2. Context Extraction (`extract_text_pypdf.py`)
- **Arguments:** 
  - `pdf_in`: Input PDF file path.
  - `md_out`: Output Markdown file path.
  - `--page-offset <N>`: Page offset for naming assets.
- **Outputs:**
  - `raw/text_pypdf.md`: Raw text dump with correct `## Page N` headers.
- **Action:** Extracts raw text from the PDF to provide a ground-truth textual context for the AI model, ensuring headers match the visual page numbers.

### 3. SKU Processing (`skus.py`)
- **Arguments:** 
  - `--input <json>`: Input Docling JSON file path.
  - `--output <jsonl>`: Output JSONL file path.
  - `--page-offset <N>`: Page offset for naming assets.
- **Outputs:**
  - `final/sku.jsonl` (Intermediate): Cleaned and structured product data.
- **Action:** Cleans and structures product data from the Docling JSON. Adds mandatory `catalog_family_context` and `series_context` to every SKU entry. Sorts chunks by Page Number (as defined by offset) and Vertical Position.

### 4. AI Synthesis (`synthesize.py`)
- **Arguments:** 
  - `export_dir`: Input directory containing assets and provenance map.
- **Outputs:**
  - `final/catalog.md`: Reconstructed Markdown catalog with missing diagrams inserted.
  - `final/sku.jsonl`: Finalized SKU dataset.
  - `final/token_usage.json`: Generation statistics.
- **Action:** Generates the final output using a multimodal LLM (Gemini 2.0 Flash). Inputs include the Page Image, Raw Text, and Provenance Map. Performs "Visual Gap Analysis" using bbox data to identify significant diagrams missing from the text and explicitly inserts them with context-aware captions.

## Usage

- you must ensure that UV_PROJECT_ENVIRONMENT is set to the cached virtual environment. If its not set, load the .env file and try again. If that fails, report to the user to create a .env file in this directory. 

**CRITICAL:** Do NOT run `uv run` locally. Use the cached virtual environment to avoid indexing issues: /Users/mat/.cache/openclaw-catalog-env/bin/python


- the output dir should be /Users/mat/.openclaw/workspace/generated/chunks/ for the sliced pdfs.
```bash
/Users/mat/.cache/openclaw-catalog-env/bin/python /Users/mat/.openclaw/workspace/skills/catalog-extractor/slice_pdf.py <input> <output> <start_page> <end_page>
```

- **MANDATORY for Chunks:** When processing a PDF chunk (e.g., from `extraction_state.json`), you **MUST** provide the `--start-page <N>` argument matching the chunk's original start page.
    - **Why?** This ensures image filenames (e.g., `page103.png`) and headers (`## Page 103`) match the original document.
    - **Failure to do so** will result in all chunks starting at "Page 1", breaking data provenance.

```bash
/Users/mat/.cache/openclaw-catalog-env/bin/python /Users/mat/.openclaw/workspace/skills/catalog-extractor/assemble_catalog.py <input_pdf> --start-page <start_page>
```

Output location:
`workspace/generated/catalog-extractor-{timestamp}`

Example:
```bash
$UV_PROJECT_ENVIRONMENT/bin/python assemble_catalog.py ../../data/catalog.pdf
```
