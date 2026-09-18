---
name: long-pdf-reader
description: Reliably index, read, resume, and answer questions from long PDFs or scanned books that do not fit safely in one model context, especially bilingual documents with formulas, tables, figures, OCR noise, or a need for page-level evidence. Use for book-scale or multi-session PDF work; ordinary short PDFs can be read directly. 长PDF可靠阅读、整本书阅读、扫描版书籍OCR处理、跨会话续读、页级证据问答、建立可恢复的证据记忆。
---

# Long PDF Reader

Treat the PDF as an evidence store, not as text to keep in conversational memory. Build a resumable external memory and load only the evidence needed for the current task.

## Runtime adaptation (WorkBuddy / Windows)

The helper script uses only the Python standard library. On this machine, invoke it with the managed interpreter instead of `python3`:

```bash
"C:/Users/yangc/.workbuddy/binaries/python/versions/3.13.12/python.exe" scripts/book_workspace.py init \
  --root <workspace> --title <title> --source <pdf-path> --pages <pdf-page-count>
```

On POSIX systems, plain `python3` remains fine. The workspace root should live under the current project directory (not the system temp directory) so it survives across sessions and can be resumed by later tasks.

## Non-negotiable invariants

1. Keep the original PDF immutable. OCR, crops, Markdown, tables, equations, and summaries are derived layers.
2. Preserve both the PDF page index and the printed page label. Never silently substitute one for the other.
3. Anchor every substantive note to source pages. Keep author statements, direct evidence, and model inference distinguishable.
4. OCR text is a search aid. For formulas, tables, plots, diagrams, marginalia, and ambiguous text, the rendered page is authoritative.
5. Never claim full-book coverage until the coverage ledger shows every in-scope page as processed or explicitly excluded.
6. Do not rely on one rolling summary. Keep immutable page/chunk notes and derive chapter and book summaries from them.
7. Save a checkpoint after each batch so a new session can resume without rereading completed pages.

## Choose the operating mode

- **Survey:** map the table of contents, chapters, terminology, and likely relevant regions. Do not imply close reading.
- **Index:** create reusable page/chunk notes and the book map for later questions.
- **Question:** retrieve a compact evidence packet for a specific query, then answer with page anchors.
- **Deep read:** exhaustively trace an argument, derivation, chapter, or topic and inspect its visuals.
- **Audit:** verify citations, formulas, tables, quotations, coverage, or an earlier answer.
- **Resume:** read the manifest, coverage ledger, book map, and session state; continue only unfinished work.

If the user gives a PDF and a specific question, default to **Survey + Question**. If they want the book available for repeated future use, default to **Index**. Ask only when the difference in time/cost or required deliverables is material.

## Workflow

### 1. Preflight the document

Record filename, stable hash when possible, page count, encryption status, page dimensions, apparent language, and whether each sampled page is born-digital, scanned, or mixed. Sample the front matter, table of contents, a body page, a visually dense page, and the end matter.

Create or reuse a persistent workspace. When scripts are available, initialize it with:

```bash
python3 scripts/book_workspace.py init \
  --root <workspace> --title <title> --source <pdf-path> --pages <pdf-page-count>
```

(See "Runtime adaptation" above for the Windows/WorkBuddy interpreter path.)

Read [references/extraction-and-ocr.md](references/extraction-and-ocr.md) when the file is scanned, mixed, bilingual, rotated, two-page-spread, or visually complex.

### 2. Build the page map before detailed reading

Identify front matter, printed page numbering, chapter boundaries, appendices, references, blank pages, foldouts, and duplicated or missing scans. Store the mapping from PDF page index to printed label and heading path.

Do not use a table of contents as proof of body content. It is navigation evidence only.

### 3. Extract in semantic batches

Prefer section boundaries over fixed token cuts. Keep a heading, its first paragraph, a formula with its definitions, and a table/figure with its caption in the same chunk when feasible. As a starting point, use roughly 6-12 ordinary A4 pages per batch, then reduce the batch for dense mathematics, tables, or poor OCR.

Limit raw page material in the working context to about one quarter of the available context. This leaves room for the book map, instructions, cross-checking, reasoning, and the answer. If a batch is still too large, split it before summarizing; do not depend on automatic context truncation.

For each chunk, save:

- stable chunk ID, PDF pages, printed pages, and heading path;
- concise summary and argument/function of the chunk;
- claims, definitions, methods, results, limitations, and cross-references;
- equations, tables, and figures that matter, with visual-verification status;
- exact short quotations only when needed, with page anchors;
- OCR/layout uncertainties, contradictions, and open questions;
- retrieval terms: Chinese/English synonyms, abbreviations, symbols, names, and index terms.

Use the templates in [references/schemas.md](references/schemas.md). Update the coverage ledger only after the chunk note is written and checked.

### 4. Consolidate without erasing provenance

After completing a chapter, synthesize its chunk notes into a chapter note. After several chapters, update the book map. Higher-level summaries should point to chunk IDs and pages; they must not replace lower-level evidence.

Track disagreements and evolution explicitly. Do not force conflicting passages into a single claim. If OCR is corrected or pagination changes, mark dependent summaries stale and rebuild them.

Read [references/memory-and-retrieval.md](references/memory-and-retrieval.md) for indexing, progressive compression, retrieval, and cross-session continuation.

### 5. Answer through an evidence packet

For each question:

1. Decompose it into concepts, aliases, symbols, people, and likely chapters.
2. Retrieve with three signals when available: lexical matches, semantic similarity, and document structure/index entries.
3. Load the book map, the best-matching chunks, and adjacent chunks needed to avoid boundary errors.
4. Render and inspect the source pages for decisive formulas, tables, figures, quotations, or low-confidence OCR.
5. Build a compact evidence packet containing supporting, qualifying, and contradictory passages.
6. Answer from that packet. Cite PDF page and printed page when known, and label any inference.
7. Record the question, evidence used, answer summary, unresolved issues, and checkpoint.

When the requested fact is not supported, say “not found in the processed evidence” and distinguish that from “not present in the book.”

## Context and memory policy

Keep only the current task, compact book map, active evidence packet, and unresolved issues in the live prompt. Persist everything else outside the conversation.

A useful default context allocation is:

- 10-15%: task, terminology, book map, and navigation;
- 45-60%: retrieved page/chunk evidence;
- 20-30%: reasoning and response construction;
- at least 10%: safety margin for tool output and corrections.

These are guardrails, not quotas. Prefer less evidence of higher relevance, plus neighboring context, over many disconnected snippets.

## Completion and quality gates

Before declaring an index complete, validate the workspace:

```bash
"C:/Users/yangc/.workbuddy/binaries/python/versions/3.13.12/python.exe" scripts/book_workspace.py validate --root <workspace>
```

Require all of the following:

- every in-scope page is accounted for exactly once in the coverage ledger;
- chapter boundaries and the two pagination systems are recorded;
- low-confidence pages are listed rather than silently accepted;
- important formulas, tables, and figures have visual-verification status;
- chapter notes link back to chunk IDs and source pages;
- the session state names the last completed batch and next action;
- the final response states the actual coverage level: surveyed, indexed, deeply read, or audited.

## Deliverable contract

For reusable reading, retain at minimum:

```text
book_manifest.json
page_map.csv
coverage.csv
book_map.md
evidence_ledger.md
session_state.md
notes/chunks/
notes/chapters/
```

Add page images, OCR text, formula crops, table extracts, or figure crops only when the source and task require them. Do not create derived files with no clear retrieval or verification purpose.
