# Extraction and OCR for long scanned PDFs

Use this reference when the PDF is scanned, mixed-content, multilingual, rotated, spread-scanned, or contains formulas, tables, plots, diagrams, or handwriting.

## 1. Classify before extracting

Sample at least:

- cover/title/copyright pages;
- table of contents;
- one ordinary body page near the beginning, middle, and end;
- a page with the densest table, equation, or figure available;
- references or index.

Classify pages as:

- **Born-digital:** reliable selectable text and vector layout.
- **Scanned:** page image with absent or unusable text layer.
- **Mixed:** image plus partial text layer, often with captions, stamps, or OCR already embedded.

Do not apply one extraction path blindly to the whole file. A single book may require all three.

## 2. Preserve an evidence master

- Keep the original PDF unchanged and record its hash when possible.
- Number derived page images by zero-padded PDF index, not printed page number.
- Store transformations and OCR settings in the manifest.
- Never discard the page image after OCR; it remains the authority for visual content.

## 3. Normalize scans conservatively

Before OCR, detect and correct:

- page rotation and upside-down pages;
- skew, perspective distortion, warped book gutters, and cropped characters;
- black borders, bleed-through, low contrast, shadows, and moire;
- two-page spreads that need splitting;
- blank, duplicated, missing, or out-of-order pages;
- color content whose meaning would be lost in grayscale.

For ordinary print, 300 dpi is a sensible starting point. Use 400-600 dpi selectively for small type, superscripts/subscripts, dense mathematics, or degraded scans. Higher resolution is not automatically better; verify the rendered result and OCR behavior.

## 4. Use language- and layout-aware OCR

- Enable the actual Chinese variant and English together when both occur.
- Preserve paragraphs, headings, columns, captions, footnotes, and reading order.
- Keep page boundaries in the OCR output.
- Store confidence or uncertainty indicators when the engine supplies them, but do not treat confidence as proof.
- Maintain a correction dictionary for recurring names, technical terms, abbreviations, and symbols.

Quality-check OCR with page images. Include random pages and all pages flagged for low confidence, unusual layout, dense notation, or many unknown characters. Look for semantic failures such as `0/O`, `1/l/I`, minus signs, decimal points, Greek letters, superscripts, subscripts, and Chinese characters with similar shapes.

## 5. Formulas

For each important equation:

1. Preserve a crop or exact page anchor.
2. Transcribe it to LaTeX or another structured form.
3. Record the equation number and nearby symbol definitions.
4. Verify operators, fraction structure, indices, exponents, accents, matrices, Greek letters, and units visually.
5. Mark the transcription `verified`, `uncertain`, or `not transcribed`.

Never derive a result from an unverified OCR formula when one changed symbol could alter the conclusion.

## 6. Tables

Keep both a page/crop reference and a structured extract when the table matters. Preserve:

- multi-row and merged headers;
- units, scaling factors, decimal marks, and missing-value notation;
- row/column order;
- footnotes and significance markers;
- continued-table relationships across pages.

Check a sample of cells against the image and reconcile totals or constraints when present. Do not infer empty cells as zero without explicit evidence.

## 7. Figures, charts, and diagrams

OCR can recover labels but not visual meaning. Inspect the rendered page and record:

- caption, panel labels, axes, units, scales, legend, and color/line encoding;
- whether values are exact labels or approximate visual readings;
- relationships conveyed only by geometry, arrows, or spatial grouping;
- whether the page must be viewed in color.

Do not invent numerical values from a plot whose resolution or scale does not support them.

## 8. Pagination

Track separately:

- `pdf_page`: physical order in the file, normally 1-based for user-facing references;
- `printed_page`: page label printed by the book, which may use Roman numerals, restart, or be absent;
- `heading_path`: chapter/section context.

If the printed label is unreadable or absent, store `unknown` rather than guessing.

## 9. OCR acceptance decision

Accept an OCR batch only when:

- reading order is usable;
- ordinary prose is semantically coherent;
- headings and page boundaries are preserved;
- decisive names, numbers, units, and symbols have been sampled against images;
- all formula/table/figure-dependent claims are separately verified or flagged.

If not, re-render or re-OCR only the affected pages with adjusted settings. Avoid rerunning an entire 400-page book when a small page class is responsible for the failure.
