# RFI Evidence Ledger — alpha-conflict-003

> **Evaluation alpha:** This output is a bounded evidence packet. It is not an engineering, contractual, schedule, cost, safety, or compliance determination.

## Run summary

| Field | Value |
|---|---|
| RFI | `RFI-044` |
| Terminal state | `conflicting_evidence` |
| Evidence claims | 0 |
| Citations | 0 |
| Receipt hash | `446d4e2c8783955338058365329098f42b342cbc22f25bc5e8d9a1f7b6927035` |

Current approved sources contain materially different firestopping requirements. The runner escalated both citations and made no interpretation.

## Evidence claims

No evidence claim was emitted. The terminal state explains why the runner stopped.

## Policy trace

- **allowed** `manifest.document_allowlist` — All bundle document keys are explicitly authorized by the task manifest.
- **allowed** `manifest.required_evidence` — All required evidence document keys are present in the authorized bundle.
- **allowed** `budget.max_documents` — Bundle contains 4 documents within the manifest budget.

## Warnings and escalations

- Conflict source A: SPEC-079200-R1 r1 — Section 07 92 00: At rated penetrations where firestopping is indicated, use tested UL system F-100.
- Conflict source B: SUBMITTAL-FIRESTOP-R2 r2 — Approved product data revision 2: Install firestop system F-200 at rated wall penetrations.

## Required human action

Review the cited evidence packet. This alpha cannot issue, submit, modify, or close an RFI.

## Source registry

```json
{
  "A-101": {
    "current_document_id": "A-101-R3",
    "current_revision": 3,
    "documents": [
      {
        "document_id": "A-101-R2",
        "revision": 2,
        "status": "superseded",
        "title": "Level 1 Life Safety Plan"
      },
      {
        "document_id": "A-101-R3",
        "revision": 3,
        "status": "current",
        "title": "Level 1 Life Safety Plan"
      }
    ]
  },
  "SPEC-079200": {
    "current_document_id": "SPEC-079200-R1",
    "current_revision": 1,
    "documents": [
      {
        "document_id": "SPEC-079200-R1",
        "revision": 1,
        "status": "current",
        "title": "Joint Sealants and Firestopping"
      }
    ]
  },
  "SUBMITTAL-FIRESTOP": {
    "current_document_id": "SUBMITTAL-FIRESTOP-R2",
    "current_revision": 2,
    "documents": [
      {
        "document_id": "SUBMITTAL-FIRESTOP-R2",
        "revision": 2,
        "status": "current",
        "title": "Firestopping Product Data"
      }
    ]
  }
}
```
