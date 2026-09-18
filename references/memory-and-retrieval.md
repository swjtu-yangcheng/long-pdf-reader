# Hierarchical memory and retrieval

## Why a long context window is not enough

A book may technically fit into a large context while still suffering from retrieval dilution, OCR noise, page-reference loss, late-context omissions, expensive rereading, and weak recovery after compression or a new session. Reliable reading therefore depends on externalized, page-addressable memory.

## Memory layers

| Layer | Contents | Mutability | Loaded when |
| --- | --- | --- | --- |
| L0 Evidence | Original PDF and page renders | Immutable | Visual verification |
| L1 Extraction | Page OCR/text, layout blocks, crops | Regenerated with versioning | Search or inspection |
| L2 Chunk memory | Page-anchored notes and retrieval terms | Append/correct with provenance | Candidate retrieval |
| L3 Chapter memory | Chapter synthesis, argument map, conflicts | Rebuilt from L2 | Navigation and cross-chapter reasoning |
| L4 Book memory | TOC, terminology, global thesis, indexes, coverage | Compact and updated | Every book-level task |
| L5 Session state | Current question, evidence packet, unresolved issues, next action | Ephemeral checkpoint | Resume current work |

Never replace L0-L2 with L3-L4. Progressive compression is useful only when provenance survives.

## Indexing pass

1. Build the PDF-to-printed-page map and heading tree.
2. Process semantic chunks in document order.
3. Write one chunk note per chunk before marking pages complete.
4. At a chapter boundary, synthesize chunk notes and list internal disagreements.
5. Update the compact book map with chapter-level pointers, terminology, and cross-references.
6. Save the next unprocessed PDF page and any special handling required.

Chunk notes should be independently retrievable. Include exact domain terms, Chinese/English equivalents, abbreviations, equation labels, figure/table numbers, people, places, standards, and alternate spellings.

## Query-time retrieval

### 1. Decompose the question

Extract:

- concepts and synonyms in both languages;
- abbreviations, names, dates, standards, variables, and formula labels;
- requested relation such as cause, comparison, definition, procedure, criticism, or chronology;
- expected evidence type: prose, table, formula, figure, or reference list.

### 2. Generate candidates

Use a combination of:

- lexical retrieval for exact terminology, numbers, symbols, and quotations;
- semantic retrieval for paraphrases and conceptual matches;
- structural retrieval from TOC, index, headings, citations, and cross-references.

Search summaries for routing, then retrieve the underlying chunks/pages for evidence. Do not answer from vector snippets or high-level summaries alone when the claim is important.

### 3. Expand locally

Add adjacent chunks or pages when a definition, derivation, table, or argument crosses a boundary. Follow explicit cross-references. Retrieve contradictory or qualifying passages, not only supporting ones.

### 4. Build the evidence packet

Keep the packet small enough to read closely. For each item, include:

- source ID and page anchors;
- relevant excerpt or faithful paraphrase;
- evidence role: supports, qualifies, contradicts, defines, or contextualizes;
- OCR/visual confidence;
- required follow-up, if any.

### 5. Synthesize and audit

State what the author says, what the evidence shows, and what the model infers. Check whether the answer overgeneralizes beyond the processed pages or the author's scope. For decisive visual evidence, reopen the rendered page before finalizing.

## Progressive compression targets

Use these only as starting ranges and expand where complexity demands:

- chunk note: 150-350 Chinese characters or 100-250 English words, plus structured evidence fields;
- chapter note: 600-1500 Chinese characters or 400-1000 English words;
- book map: 1000-2500 Chinese characters or 700-1700 English words, plus indexes.

Do not meet a length target by deleting qualifications, page anchors, conflicts, or uncertainty.

## Resuming after interruption or context compaction

Load, in order:

1. `book_manifest.json`;
2. `session_state.md`;
3. `coverage.csv` and `page_map.csv` around the next page;
4. `book_map.md`;
5. the last completed chunk and chapter note;
6. only the source pages needed for the next batch.

Verify the source hash or identity before continuing. If it changed, stop and reconcile pagination/version differences.

## Updating memory safely

- Corrections are explicit; do not silently rewrite evidence history.
- If a page extraction changes materially, mark downstream chunk/chapter/book summaries stale.
- Keep unresolved OCR, pagination, and interpretation issues in the session state and evidence ledger.
- Record scope precisely: `surveyed`, `OCR extracted`, `chunk indexed`, `chapter synthesized`, or `visually audited` are different states.

## Common failure patterns

- Sequentially pasting the entire book into chat and assuming recall.
- Repeatedly replacing detailed notes with a shorter rolling summary.
- Splitting solely by token count and separating captions or definitions from their objects.
- Treating OCR confidence as correctness.
- Answering from retrieved snippets without neighboring context.
- Calling a TOC scan or vector index “full reading.”
- Losing the distinction between PDF page and printed page.
