# RFI Evidence Ledger — alpha-supported-001

> **Evaluation alpha:** This output is a bounded evidence packet. It is not an engineering, contractual, schedule, cost, safety, or compliance determination.

## Run summary

| Field | Value |
|---|---|
| RFI | `RFI-042` |
| Terminal state | `evidence_packet_ready` |
| Evidence claims | 2 |
| Citations | 2 |
| Receipt hash | `f9c4e832878e2bdd90a9961ebee5ca51115ed7c0d4de22af7e0a279f2404e90d` |

Current drawing and specification sources were cited and replay-validated. A human project manager must still determine any official RFI response.

## Evidence claims

### C-001 — drawing_detail

Verified current drawing evidence: Revision 3 detail D7: Provide listed firestop system F-100 at rated wall penetrations.

- **Source:** `A-101-R3` revision `3`, `A-101` / `detail D7`
- **Source text:** Revision 3 detail D7: Provide listed firestop system F-100 at rated wall penetrations.

### C-002 — specification_requirement

Verified current specification evidence: Section 07 92 00: At rated penetrations where firestopping is indicated, use tested UL system F-100.

- **Source:** `SPEC-079200-R1` revision `1`, `07 92 00` / `governing requirement`
- **Source text:** Section 07 92 00: At rated penetrations where firestopping is indicated, use tested UL system F-100.

## Policy trace

- **allowed** `manifest.document_allowlist` — All bundle document keys are explicitly authorized by the task manifest.
- **allowed** `manifest.required_evidence` — All required evidence document keys are present in the authorized bundle.
- **allowed** `budget.max_documents` — Bundle contains 4 documents within the manifest budget.

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
