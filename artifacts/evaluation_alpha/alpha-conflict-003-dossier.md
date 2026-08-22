# RFI Evidence Ledger — alpha-conflict-003

> **Evaluation alpha:** This output is a bounded evidence packet. It is not an engineering, contractual, schedule, cost, safety, or compliance determination.

## Run summary

| Field | Value |
|---|---|
| RFI | `RFI-044` |
| Terminal state | `conflicting_evidence` |
| Evidence claims | 0 |
| Citations | 0 |
| Receipt hash | `15738a265c30dcca9ef4bcf7ad44c2e2d9e284f8775591d214ddd9592a77bc64` |

Current approved sources contain materially different firestopping requirements. The runner escalated both citations and made no interpretation.

## Evidence claims

No evidence claim was emitted. The terminal state explains why the runner stopped.

## Policy trace

- **allowed** `manifest.document_allowlist` — All bundle document keys are explicitly authorized by the task manifest.
- **allowed** `manifest.required_evidence` — All required evidence document keys are present in the authorized bundle.
- **allowed** `budget.max_documents` — Bundle contains 4 documents within the manifest budget.

## Execution graph

**Mode:** `bounded_local_fan_in` — only independent required-source checks may run concurrently.

- `intake` ← root — Load one approved task manifest and one local versioned bundle.
- `policy_preflight` ← intake — Fail closed on bundle allowlist, required-evidence, and document-budget violations.
- `source_preflight_fan` ← intake — Check each independent required source key locally, then join results in sorted manifest order.
- `scenario_evidence` ← policy_preflight, source_preflight_fan — Construct only the bounded scenario evidence permitted by the manifest.
- `citation_replay` ← scenario_evidence — Replay every citation against the current approved source registry.
- `human_review` ← citation_replay — Require a human project decision; the alpha cannot issue or change an RFI.

**Route trace:**
- `conflict_stop` — Current approved sources disagree and the runner will not interpret the conflict.

## Required-source preflight

- `SPEC-079200` — `ready`; current revision: `1`; A current approved revision is available in the authorized local bundle.
- `SUBMITTAL-FIRESTOP` — `ready`; current revision: `2`; A current approved revision is available in the authorized local bundle.

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
