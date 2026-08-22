#!/usr/bin/env python3
"""Run all bundled evaluation-alpha manifests without network or model access."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rfi_evidence_ledger.artifacts import write_artifacts
from rfi_evidence_ledger.intake import load_bundle, load_task
from rfi_evidence_ledger.runner import run

CASES = {
    "supported_evidence.json": "evidence_packet_ready",
    "stale_revision.json": "stale_revision_detected",
    "conflicting_evidence.json": "conflicting_evidence",
    "missing_source.json": "missing_source",
    "policy_blocked.json": "policy_blocked",
}


def main() -> int:
    artifact_dir = ROOT / "artifacts" / "evaluation_alpha"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for manifest_name, expected_state in CASES.items():
        task = load_task(ROOT / "examples" / manifest_name)
        documents = load_bundle(ROOT / task.bundle_path)
        outcome = run(task, documents)
        paths = write_artifacts(outcome, artifact_dir)
        passed = outcome.terminal_state.value == expected_state
        rows.append(
            {
                "manifest": manifest_name,
                "expected_terminal_state": expected_state,
                "actual_terminal_state": outcome.terminal_state.value,
                "result": "PASS" if passed else "FAIL",
                "dossier": str(paths["dossier"].relative_to(ROOT)),
                "receipt": str(paths["receipt"].relative_to(ROOT)),
            }
        )
    matrix = {"schema_version": "1.0", "network_used": False, "model_used": False, "cases": rows}
    (artifact_dir / "evaluation-matrix.json").write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# RFI Evidence Ledger — Evaluation Alpha Matrix",
        "",
        "> This matrix reports deterministic fixture outcomes. It is not a real-project accuracy or savings claim.",
        "",
        "| Manifest | Expected terminal state | Actual terminal state | Result |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['manifest']}` | `{row['expected_terminal_state']}` | `{row['actual_terminal_state']}` | **{row['result']}** |"
        )
    lines.extend(
        [
            "",
            "The evaluator used no network, no model provider, no browser session, and no external project-system connection.",
            "",
        ]
    )
    (artifact_dir / "evaluation-matrix.md").write_text("\n".join(lines), encoding="utf-8")
    failures = [row for row in rows if row["result"] != "PASS"]
    print(f"evaluation_cases={len(rows)} passed={len(rows) - len(failures)} failed={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
