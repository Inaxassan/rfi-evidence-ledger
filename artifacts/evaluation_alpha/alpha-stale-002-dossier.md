# RFI Evidence Ledger — alpha-stale-002

> **Evaluation alpha:** This output is a bounded evidence packet. It is not an engineering, contractual, schedule, cost, safety, or compliance determination.

## Run summary

| Field | Value |
|---|---|
| RFI | `RFI-043` |
| Terminal state | `stale_revision_detected` |
| Evidence claims | 0 |
| Citations | 0 |
| Receipt hash | `4e6d25259c00876a599c135c0a73ba3be0cdb9a641eb5bea61774d7c3eb474b6` |

A-101-R2 revision 2 is superseded by A-101-R3 revision 3; the runner will not use it as governing evidence.

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
- `stale_revision_stop` — The requested source is superseded and cannot govern evidence.

## Required-source preflight

- `A-101` — `ready`; current revision: `3`; A current approved revision is available in the authorized local bundle.

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
