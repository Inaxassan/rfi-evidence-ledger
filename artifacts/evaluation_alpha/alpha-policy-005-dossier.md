# RFI Evidence Ledger — alpha-policy-005

> **Evaluation alpha:** This output is a bounded evidence packet. It is not an engineering, contractual, schedule, cost, safety, or compliance determination.

## Run summary

| Field | Value |
|---|---|
| RFI | `RFI-046` |
| Terminal state | `policy_blocked` |
| Evidence claims | 0 |
| Citations | 0 |
| Receipt hash | `8f09fe5309895c7c1e5ee7768dbae8d1f6aaf42387b44da4e58b29f3b093d2db` |

The runner stopped before evidence generation because the approved manifest boundary was not satisfied.

## Evidence claims

No evidence claim was emitted. The terminal state explains why the runner stopped.

## Policy trace

- **blocked** `manifest.document_allowlist` — Bundle contains unauthorized document keys: SUBMITTAL-FIRESTOP
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
- `policy_stop` — The manifest boundary or document budget was not satisfied before evidence generation.

## Required-source preflight

- `A-101` — `ready`; current revision: `3`; A current approved revision is available in the authorized local bundle.
- `SPEC-079200` — `ready`; current revision: `1`; A current approved revision is available in the authorized local bundle.

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
