# Workspace schemas and templates

Use stable, plain-text artifacts so any agent can inspect and resume the work. JSON/CSV are for state and coverage; Markdown is for human-readable memory.

## Recommended tree

```text
<book-workspace>/
├── book_manifest.json
├── page_map.csv
├── coverage.csv
├── book_map.md
├── evidence_ledger.md
├── session_state.md
├── source/
├── pages/
│   ├── text/
│   └── images/
├── notes/
│   ├── chunks/
│   └── chapters/
└── assets/
    ├── equations/
    ├── tables/
    └── figures/
```

## `book_manifest.json`

```json
{
  "schema_version": "1.0",
  "title": "",
  "source_path": "",
  "source_sha256": "",
  "pdf_pages": 0,
  "languages": ["zh", "en"],
  "document_type": "unknown",
  "created_at": "",
  "updated_at": "",
  "extraction": {
    "text_layer": "unknown",
    "ocr_engine": "",
    "ocr_settings": "",
    "render_settings": ""
  }
}
```

Use `document_type`: `born-digital`, `scanned`, `mixed`, or `unknown`.

## `page_map.csv`

```csv
pdf_page,printed_page,heading_path,page_type,notes
1,,Front matter,cover,
2,i,Front matter,title,
```

Keep one row per PDF page. `printed_page` may be blank or `unknown`; never derive it from PDF position without evidence.

## `coverage.csv`

```csv
pdf_page,status,chunk_id,ocr_status,visual_status,updated_at,notes
1,pending,,not_run,not_checked,,
```

Recommended values:

- `status`: `pending`, `excluded`, `surveyed`, `indexed`, `audited`;
- `ocr_status`: `not_needed`, `not_run`, `ok`, `uncertain`, `failed`;
- `visual_status`: `not_needed`, `not_checked`, `checked`, `uncertain`.

An `excluded` page needs a reason in `notes`.

## Chunk note

Filename: `notes/chunks/CH<chapter>_C<sequence>_P<start>-<end>.md`

```markdown
---
chunk_id: CH03_C007
pdf_pages: 121-128
printed_pages: 103-110
heading_path: Chapter 3 > 3.4 > Mechanism
source_sha256: ""
extraction_version: ""
status: indexed
---

# Function in the book

# Concise summary

# Evidence

| Claim / definition / result | Evidence role | PDF page | Printed page | Confidence |
| --- | --- | ---: | --- | --- |

# Equations, tables, and figures

| ID | Meaning | Page | Visual status | Notes |
| --- | --- | ---: | --- | --- |

# Retrieval terms

- Chinese terms:
- English terms:
- Symbols / abbreviations:
- Names / standards:

# Qualifications, conflicts, and open questions
```

## Chapter note

```markdown
# Chapter <n>: <title>

- Scope:
- Source chunks:
- PDF pages:
- Printed pages:

## Chapter purpose and argument

## Key concepts and definitions

## Methods / evidence / results

## Important equations, tables, and figures

## Qualifications and internal tensions

## Links to other chapters

## Unresolved items
```

## `book_map.md`

```markdown
# Book map

## Identity and coverage

## Pagination map

## Heading tree

## Global thesis and scope

## Chapter map

| Chapter | Purpose | Key topics | PDF pages | Note |
| --- | --- | --- | --- | --- |

## Terminology and bilingual aliases

## Equation / table / figure index

## Cross-chapter themes and conflicts

## Known extraction or coverage limitations
```

## `evidence_ledger.md`

```markdown
# Evidence ledger

| Evidence ID | Claim or question | Source pages / chunks | Role | Verification | Notes |
| --- | --- | --- | --- | --- | --- |
```

Use roles such as `supports`, `qualifies`, `contradicts`, `defines`, and `contextualizes`.

## `session_state.md`

```markdown
# Session state

- Source identity/hash:
- Operating mode:
- Actual coverage level:
- Last completed batch:
- Next PDF page / chunk:
- Current question:
- Active evidence packet:
- Low-confidence pages:
- Unresolved issues:
- Stale derived notes:
- Next action:
- Updated at:
```

Keep this short. It is a restart pointer, not another book summary.
