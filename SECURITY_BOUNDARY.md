# Security and Capability Boundary

## Core rule

> **RFI Evidence Ledger can prepare local evidence artifacts. It cannot take an external project action.**

The evaluation alpha is intentionally a small offline runner. Its safety boundary is structural: the package contains no network client, no browser control, no model-provider client, no project-system SDK, no email sender, no credentials, and no write-capable connector. Policy checks and verifier checks are deterministic Python code outside any model.

## Allowed capabilities

| Capability | Alpha behavior |
|---|---|
| Read local task manifest | Strict JSON, unknown fields rejected. |
| Read local fixture bundle | Only from an evaluator-selected local path. |
| Build a revision registry | Uses declared document key, revision, status, and source regions. |
| Produce local evidence artifacts | Writes dossier and JSON receipt only to caller-selected local output directory. |
| Run deterministic verification | Replays citation identity, current revision, and source region. |

## Denied capabilities

| Capability | Why it is denied |
|---|---|
| Network or public-web access | Prevents unapproved retrieval and data egress. |
| Email, chat, or external notifications | Prevents the alpha from communicating with project stakeholders. |
| Project-system access | Prevents creation, modification, routing, submission, or closure of project records. |
| Cloud storage / drive sync | Prevents ambient access to drawings, RFIs, or specifications. |
| Browser sessions | Prevents access to authenticated customer tools. |
| Model-provider calls | Keeps the alpha deterministic, offline, and free of customer-data egress. |
| Cost, schedule, contract, code, safety, or engineering decision | These require accountable human professional judgment. |

## Threat model

| Threat | Alpha control | Expected terminal behavior |
|---|---|---|
| Unauthorized document included in a task bundle | Manifest allowlist checks every document key before evidence generation. | `policy_blocked` |
| Expected source missing | Required document keys are checked before evidence generation. | `missing_source` |
| Superseded drawing used as evidence | Revision registry identifies the sole current document for a document key. | `stale_revision_detected` |
| Current sources conflict | The fixture scenario lists both sources without selecting an interpretation. | `conflicting_evidence` |
| Fabricated or stale citation | Independent verifier replays document/revision/region/source text. | `verification_failed` when a claim cannot be replayed. |
| Manifest tampering / unexpected field | Strict intake rejects unknown or malformed fields. | `intake_rejected` |
| Runaway input or output size | Manifest document and output-claim budgets are checked deterministically. | `policy_blocked` |
| Instruction-like text in source documents | This alpha has no model or tool executor. Future versions must treat retrieved document content as data, never instructions. | Safe design requirement before a model is added. |

## Human responsibility

A project manager, designer, engineer, or other qualified accountable reviewer must decide whether a cited source is relevant to the real RFI and whether any formal response or project action should occur. The evidence packet is not an approval, instruction, recommendation, professional opinion, or construction determination.

## Future pilot conditions

A future model-enabled or connected pilot must add controls beyond this alpha: named user identity; customer-approved data classification; per-run document manifest; short-lived read-only access; redaction and retention policy; provider egress approval; prompt-injection handling; independent claim/citation verification; audit trace; and a deliberate human decision receipt. Those features are designed in the documentation but are not represented as implemented in this alpha.
