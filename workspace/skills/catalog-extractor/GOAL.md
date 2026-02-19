# Goal: High-Fidelity Catalog Extraction

## Objective
Create a "Perfect Ground Truth" dataset from technical product catalogs (PDFs) that captures both the **visual narrative** (`catalog.md`) and the **structured data** (`sku.jsonl`) with absolute fidelity and provenance.

## Core Philosophy
**"Multimodal Backbone, Structured Details"**
We do not rely on brittle Python heuristics (e.g., "if line starts with 'Part No'") to parse complex documents. Instead, we use Python to extract high-quality "raw ingredients" and rely on an AI Synthesis layer to reconstruct the document logic using visual and textual cues.

## The Pipeline

### 1. Extract Ingredients (Python)
We decouple extraction into three verifiable streams. Every stream **MUST** preserve provenance (Page Number, Bounding Box).

*   **Text Stream (`raw/text_stream.jsonl`)**:
    *   **Content**: All text blocks (Headers, Paragraphs, Footers, Sidebars).
    *   **Provenance**: Explicit `page_no` and `bbox` for every item.
    *   **Goal**: Capture the "narrative" that surrounds the data (Marketing, Compliance, Hierarchy).
*   **Table Grid (`raw/tables_raw.md`)**:
    *   **Content**: Structural grids extracted using `TableFormerMode.ACCURATE`.
    *   **Provenance**: Wrapped in `<!-- Page N -->` markers.
    *   **Goal**: Capture the rigid technical specs without OCR noise.
*   **Visual Ground Truth (`raw/images/`)**:
    *   **Content**: Full-page screenshots (`pageN.png`) and diagram crops.
    *   **Goal**: Provide the "Visual Context" for the AI to resolve ambiguity (e.g., "Is this a header or a footer?").

### 2. AI Synthesis (LLM)
(Future Step)
An LLM consumes the "Ingredients" to generate the final artifacts.
*   **Input**: `pageN.png` + Text Stream (Page N) + Table Data (Page N).
*   **Task**:
    *   Reconstruct broken text ("Indus-" + "trial").
    *   Link Context to Data (e.g., Apply "Xtra-Guard 1" header to the table below it).
    *   Filter noise ("llenge") by comparing OCR with Visuals.

## Target Outputs

### `catalog.md` (The Document)
A linear, readable Markdown document organized by **Page**.
*   **Visuals**: Starts with `![Page N](pageN.png)`.
*   **Context**: Clean headers and paragraphs explaining the products.
*   **Data**: Cleaned markdown tables.
*   **Provenance**: Strictly ordered by page flow.

### `sku.jsonl` (The Database)
A machine-readable dataset of every product.
*   **Records**: `product_sku` (and optionally `series_context` if useful).
*   **Fields**: `sku`, `specs`, `series`, `description`.
*   **Provenance (CRITICAL)**: Every record MUST include:
    ```json
    "provenance": { "page": 3, "file": "catalog.pdf", "bbox": [...] }
    ```

## Constraints
1.  **No Data Loss**: Never drop a table because it "doesn't look like a SKU list". Extract it, let the AI label it.
2.  **Visual Verification**: Every data point should be visually verifiable against the `pageN.png`.
