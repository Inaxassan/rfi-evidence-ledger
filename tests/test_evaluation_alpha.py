from __future__ import annotations

import json
from pathlib import Path

import pytest

from rfi_evidence_ledger.artifacts import build_receipt, write_artifacts
from rfi_evidence_ledger.intake import IntakeError, load_bundle, load_task
from rfi_evidence_ledger.models import Citation, EvidenceClaim, TerminalState
from rfi_evidence_ledger.registry import RevisionRegistry
from rfi_evidence_ledger.runner import run
from rfi_evidence_ledger.verifier import verify_claims

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "fixtures" / "project_alpha" / "document_bundle.json"


def outcome_for(manifest_name: str):
    task = load_task(ROOT / "examples" / manifest_name)
    return run(task, load_bundle(ROOT / task.bundle_path))


@pytest.mark.parametrize(
    ("manifest_name", "expected_state"),
    [
        ("supported_evidence.json", TerminalState.EVIDENCE_PACKET_READY),
        ("stale_revision.json", TerminalState.STALE_REVISION_DETECTED),
        ("conflicting_evidence.json", TerminalState.CONFLICTING_EVIDENCE),
        ("missing_source.json", TerminalState.MISSING_SOURCE),
        ("policy_blocked.json", TerminalState.POLICY_BLOCKED),
    ],
)
def test_all_bundled_scenarios_end_in_expected_state(manifest_name: str, expected_state: TerminalState):
    assert outcome_for(manifest_name).terminal_state is expected_state


def test_supported_evidence_has_two_current_replayable_claims():
    outcome = outcome_for("supported_evidence.json")
    assert len(outcome.claims) == 2
    registry = RevisionRegistry(load_bundle(BUNDLE))
    assert all(finding.valid for finding in verify_claims(outcome.claims, registry))
    assert {claim.citations[0].revision for claim in outcome.claims} == {1, 3}


def test_stale_revision_is_not_used_as_a_claim():
    outcome = outcome_for("stale_revision.json")
    assert not outcome.claims
    assert "superseded" in outcome.summary
    assert outcome.registry["A-101"]["current_revision"] == 3


def test_conflict_is_exposed_without_interpretation():
    outcome = outcome_for("conflicting_evidence.json")
    assert not outcome.claims
    assert len(outcome.warnings) == 2
    assert "F-100" in outcome.warnings[0]
    assert "F-200" in outcome.warnings[1]


def test_verifier_rejects_a_superseded_citation():
    documents = load_bundle(BUNDLE)
    registry = RevisionRegistry(documents)
    stale = registry.requested("A-101", 2)
    assert stale is not None
    region = stale.regions[0]
    citation = Citation(stale.document_id, stale.document_key, stale.revision, region.page_or_sheet, region.region_label, region.text)
    claim = EvidenceClaim("C-stale", "drawing_detail", f"Verified source statement: {region.text}", (citation,))
    findings = verify_claims([claim], registry)
    assert findings[0].valid is False
    assert "superseded" in findings[0].reason


def test_receipt_is_hashed_and_artifacts_are_written(tmp_path: Path):
    outcome = outcome_for("supported_evidence.json")
    receipt = build_receipt(outcome)
    assert len(receipt["receipt_sha256"]) == 64
    paths = write_artifacts(outcome, tmp_path)
    assert paths["dossier"].exists()
    saved_receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
    assert saved_receipt["terminal_state"] == "evidence_packet_ready"


def test_unknown_manifest_field_is_rejected(tmp_path: Path):
    source = json.loads((ROOT / "examples" / "supported_evidence.json").read_text(encoding="utf-8"))
    source["untrusted_field"] = "do not accept me"
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(IntakeError, match="Unknown task fields"):
        load_task(invalid)
