"""Evidence dossier and run-receipt generation for the local evaluation alpha."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .models import EvidenceOutcome

PACKAGE_VERSION = "0.1.0a0"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_receipt(outcome: EvidenceOutcome) -> dict[str, Any]:
    """Build a portable receipt without persisting unneeded fixture internals."""

    task = outcome.task.to_dict()
    registry = outcome.registry
    receipt = {
        "schema_version": "1.0",
        "runner": {"name": "rfi-evidence-ledger", "version": PACKAGE_VERSION},
        "task_id": outcome.task.task_id,
        "rfi_id": outcome.task.rfi_id,
        "terminal_state": outcome.terminal_state.value,
        "summary": outcome.summary,
        "task_manifest_sha256": _canonical_hash(task),
        "source_registry_sha256": _canonical_hash(registry),
        "allowed_document_keys": list(outcome.task.allowed_document_keys),
        "required_document_keys": list(outcome.task.required_document_keys),
        "policy_events": [event.to_dict() for event in outcome.policy_events],
        "claim_count": len(outcome.claims),
        "citation_count": sum(len(claim.citations) for claim in outcome.claims),
        "warnings": outcome.warnings,
        "elapsed_seconds": outcome.elapsed_seconds,
        "required_human_action": "Review the cited evidence packet. This alpha cannot issue, submit, modify, or close an RFI.",
    }
    receipt["receipt_sha256"] = _canonical_hash(receipt)
    return receipt


def _dossier_text(outcome: EvidenceOutcome, receipt: dict[str, Any]) -> str:
    lines = [
        f"# RFI Evidence Ledger — {outcome.task.task_id}",
        "",
        "> **Evaluation alpha:** This output is a bounded evidence packet. It is not an engineering, contractual, schedule, cost, safety, or compliance determination.",
        "",
        "## Run summary",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| RFI | `{outcome.task.rfi_id}` |",
        f"| Terminal state | `{outcome.terminal_state.value}` |",
        f"| Evidence claims | {len(outcome.claims)} |",
        f"| Citations | {receipt['citation_count']} |",
        f"| Receipt hash | `{receipt['receipt_sha256']}` |",
        "",
        outcome.summary,
        "",
        "## Evidence claims",
        "",
    ]
    if outcome.claims:
        for claim in outcome.claims:
            lines.extend([f"### {claim.claim_id} — {claim.claim_type}", "", claim.text, ""])
            for citation in claim.citations:
                lines.extend(
                    [
                        f"- **Source:** `{citation.document_id}` revision `{citation.revision}`, `{citation.page_or_sheet}` / `{citation.region_label}`",
                        f"- **Source text:** {citation.source_text}",
                    ]
                )
            lines.append("")
    else:
        lines.extend(["No evidence claim was emitted. The terminal state explains why the runner stopped.", ""])
    lines.extend(["## Policy trace", ""])
    for event in outcome.policy_events:
        verdict = "allowed" if event.allowed else "blocked"
        lines.append(f"- **{verdict}** `{event.rule}` — {event.reason}")
    lines.append("")
    if outcome.warnings:
        lines.extend(["## Warnings and escalations", ""])
        lines.extend(f"- {warning}" for warning in outcome.warnings)
        lines.append("")
    lines.extend(
        [
            "## Required human action",
            "",
            receipt["required_human_action"],
            "",
            "## Source registry",
            "",
            "```json",
            json.dumps(outcome.registry, indent=2, sort_keys=True),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts(outcome: EvidenceOutcome, output_dir: Path) -> dict[str, Path]:
    """Write a receipt and dossier to a caller-selected local directory."""

    output_dir.mkdir(parents=True, exist_ok=True)
    receipt = build_receipt(outcome)
    receipt_path = output_dir / f"{outcome.task.task_id}-receipt.json"
    dossier_path = output_dir / f"{outcome.task.task_id}-dossier.md"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    dossier_path.write_text(_dossier_text(outcome, receipt).rstrip() + "\n", encoding="utf-8")
    return {"receipt": receipt_path, "dossier": dossier_path}
