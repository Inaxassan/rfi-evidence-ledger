# RFI Evidence Ledger Evaluation Checklist

> **Estimated effort:** 10 minutes. This offline evaluation requires Python 3 and does not require an account, API key, network connection, or customer document.

## Before you start

Confirm that you understand the scope: this repository demonstrates a deterministic **evidence-control harness** on a transparent fixture. It does not demonstrate an LLM, real PDF/drawing analysis, construction judgment, production integration, or autonomous RFI work.

## 1. Run the tests

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
```

**Expected:** all tests pass. The suite covers strict manifest intake, allowed-source policy, revision state, citations, verifier rejection of a stale citation, receipts, and all five bundled scenarios.

## 2. Run every controlled scenario

```bash
python3 scripts/verify_evaluation_alpha.py
cat artifacts/evaluation_alpha/evaluation-matrix.md
```

**Expected:** five passing cases and the following terminal states.

| Manifest | Expected state | Check |
|---|---|---|
| `supported_evidence.json` | `evidence_packet_ready` | The dossier contains two claims with current source citations. |
| `stale_revision.json` | `stale_revision_detected` | Revision 2 of drawing A-101 is identified as superseded by revision 3. |
| `conflicting_evidence.json` | `conflicting_evidence` | The runner surfaces F-100 and F-200 as conflicting current-source statements and makes no interpretation. |
| `missing_source.json` | `missing_source` | The runner stops because `S-501` is not in the approved bundle. |
| `policy_blocked.json` | `policy_blocked` | The fixture bundle contains an unauthorized document key under that manifest. |

## 3. Inspect a verified evidence packet

```bash
cat artifacts/evaluation_alpha/alpha-supported-001-dossier.md
cat artifacts/evaluation_alpha/alpha-supported-001-receipt.json
```

Verify that each claim cites a document ID, revision, page/sheet, region label, and exact source text. The receipt should include task and source-registry hashes, policy events, citation count, terminal state, and the mandatory human next action.

## 4. Check that the stale drawing is not treated as governing

```bash
cat artifacts/evaluation_alpha/alpha-stale-002-dossier.md
```

Verify that the dossier names `A-101-R2` as superseded by `A-101-R3` and contains no evidence claim using the old revision.

## 5. Check that conflict is not turned into an answer

```bash
cat artifacts/evaluation_alpha/alpha-conflict-003-dossier.md
```

Verify that the dossier lists both conflicting sources as warnings, has no evidence claim, and asks a human to resolve the conflict.

## 6. Check the no-action boundary

Review [`ALPHA_BOUNDARY.md`](ALPHA_BOUNDARY.md) and [`SECURITY_BOUNDARY.md`](SECURITY_BOUNDARY.md). The package contains no network client, model provider client, browser automation, email sender, project-system connector, write operation, or credential mechanism.

## 7. Leave useful technical feedback

If you find a reproducible defect, submit an issue using the technical-evaluation template. Please include the command, Python version, expected terminal state, actual output, and non-confidential reproduction detail. Do **not** upload drawings, specifications, RFIs, credentials, or customer records.
