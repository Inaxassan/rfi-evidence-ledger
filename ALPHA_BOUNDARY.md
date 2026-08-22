# RFI Evidence Ledger — Evaluation Alpha Boundary

## What this alpha demonstrates

RFI Evidence Ledger is a **bounded construction-document evidence runner**. Given one approved RFI task and one local, versioned document bundle, it creates a source registry, detects current/superseded revisions, validates document access against a manifest, and emits an evidence packet with source citations and explicit safe-stop states.

The bundled fixture is deterministic and offline. It proves the evaluation harness, source registry, policy boundary, revision checks, and evidence-artifact format. It does **not** prove real-world performance on construction drawings, PDFs, scanned documents, contracts, project-management systems, or customer data.

## What it does not do

The alpha does not call a model provider, access a network, parse production PDFs or CAD/BIM files, search the public web, access email, access browser sessions, connect to Procore/SharePoint/Drive, submit an RFI, modify a document, create a change order, calculate cost or schedule impact, or make an engineering, contract, safety, or compliance decision.

A future customer-controlled pilot may add a model and layout-aware parser only after the customer approves data handling, document scope, provider egress, retention, and a human-review procedure.

## Non-negotiable rule

> The harness decides which sources may be read and which artifact may be written. The evaluator—not the model—decides whether any project action occurs.

## Terminal states

| State | Meaning |
|---|---|
| `evidence_packet_ready` | The selected fixture claim has valid current-source evidence; human review remains required. |
| `stale_revision_detected` | A requested source exists but is superseded by a later approved revision. |
| `conflicting_evidence` | Current approved sources disagree on a material term; the runner escalates rather than resolving it. |
| `missing_source` | An expected source was not supplied in the authorized bundle. |
| `policy_blocked` | A task requested a source outside the signed manifest or violated a configured boundary. |
| `verification_failed` | A proposed evidence claim could not be replayed against a current approved source. |
| `intake_rejected` | The task or document bundle is malformed or incomplete. |

## Release position

This is an **evaluation alpha**, not a production offering or an autonomous construction agent. It is not validated on a customer project, does not have paid users, and makes no ROI, accuracy, time-saving, or safety claim.
