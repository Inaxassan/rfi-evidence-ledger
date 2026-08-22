# RFI Evidence Ledger v0.1.0-alpha

## Evaluation-alpha release

RFI Evidence Ledger v0.1.0-alpha is the first public evaluation package for a bounded construction-document evidence runner. It is intended for technical review of the runner’s task contract, local source policy, revision registry, citation artifact format, independent replay verification, and safe-stop behavior.

## Included

| Included capability | Evidence in this release |
|---|---|
| Strict local task manifests | Five transparent JSON manifests in `examples/`. |
| Versioned local source bundle | Current and superseded document revisions plus a controlled source conflict in `fixtures/project_alpha/`. |
| Document-access policy | Allowlist and required-evidence checks with audit events. |
| Revision-aware safe stops | Controlled stale, missing, conflict, and policy-blocked cases. |
| Cited evidence artifacts | Per-run Markdown dossier and JSON receipt with hashes. |
| Independent citation replay | Verifier confirms document/revision/region/source-text identity and rejects superseded citations. |
| One-command evaluator | `python3 scripts/verify_evaluation_alpha.py` generates a factual five-case matrix. |
| Brand and evaluator materials | Logo assets, GitHub share card, README, architecture, boundary, security, and checklist documents. |

## Validated locally before release preparation

The local package test suite and the five-scenario offline evaluation pack are required to pass before publication. The release archive should include the source, fixture, generated evaluation artifacts, and a SHA-256 checksum.

## Not included

This alpha does not include a language-model call, OCR/PDF/CAD parser, real construction drawing, customer project data, user authentication, hosted service, cloud storage, model-provider integration, public-web access, browser access, Procore/SharePoint/Drive integration, email, RFI submission, document modification, project-system write action, cost/schedule calculation, or engineering/contract/safety decision.

## Known limitations

The fixture is deliberately small and deterministic. It proves the local control and artifact mechanics only. It is not a benchmark, customer case study, real-project evaluation, accuracy claim, ROI claim, or production-readiness claim. A future pilot must be customer-approved, document-only at first, and evaluated on historical closed RFI cases with accountable human review.
