"""A small offline runner for deterministic construction-document evidence evaluation."""

from __future__ import annotations

from time import perf_counter

from .models import Citation, EvidenceClaim, EvidenceOutcome, ProjectDocument, TaskSpec, TerminalState
from .policy import evaluate_bundle_policy, policy_allows
from .registry import RevisionRegistry
from .verifier import verify_claims


def _region(document: ProjectDocument, label: str):
    for region in document.regions:
        if region.region_label == label:
            return region
    raise ValueError(f"Fixture source region {label!r} does not exist in {document.document_id}")


def _citation(document: ProjectDocument, label: str) -> Citation:
    region = _region(document, label)
    return Citation(
        document_id=document.document_id,
        document_key=document.document_key,
        revision=document.revision,
        page_or_sheet=region.page_or_sheet,
        region_label=region.region_label,
        source_text=region.text,
    )


def _safe_outcome(
    state: TerminalState,
    summary: str,
    task: TaskSpec,
    registry: RevisionRegistry,
    decisions,
    started: float,
    warnings: list[str] | None = None,
) -> EvidenceOutcome:
    return EvidenceOutcome(
        terminal_state=state,
        summary=summary,
        task=task,
        registry=registry.snapshot(),
        policy_events=list(decisions),
        warnings=warnings or [],
        elapsed_seconds=round(perf_counter() - started, 6),
    )


def run(task: TaskSpec, documents: tuple[ProjectDocument, ...]) -> EvidenceOutcome:
    """Run one deterministic evaluation-alpha task without model calls or network access."""

    started = perf_counter()
    registry = RevisionRegistry(documents)
    decisions = evaluate_bundle_policy(task, documents)
    if not policy_allows(decisions):
        required_missing = any(
            not decision.allowed and decision.rule == "manifest.required_evidence" for decision in decisions
        )
        state = TerminalState.MISSING_SOURCE if required_missing else TerminalState.POLICY_BLOCKED
        return _safe_outcome(
            state,
            "The runner stopped before evidence generation because the approved manifest boundary was not satisfied.",
            task,
            registry,
            decisions,
            started,
        )

    if task.scenario == "stale_revision":
        if task.requested_revision is None:
            return _safe_outcome(
                TerminalState.INTAKE_REJECTED,
                "The stale-revision scenario requires an explicit requested revision.",
                task,
                registry,
                decisions,
                started,
            )
        document_key, revision = task.requested_revision
        requested = registry.requested(document_key, revision)
        current = registry.current(document_key)
        if requested is None:
            return _safe_outcome(
                TerminalState.MISSING_SOURCE,
                f"Requested document {document_key} revision {revision} was not supplied in the approved bundle.",
                task,
                registry,
                decisions,
                started,
            )
        if current is not None and not registry.is_current(requested):
            return _safe_outcome(
                TerminalState.STALE_REVISION_DETECTED,
                f"{requested.document_id} revision {requested.revision} is superseded by {current.document_id} revision {current.revision}; the runner will not use it as governing evidence.",
                task,
                registry,
                decisions,
                started,
            )
        return _safe_outcome(
            TerminalState.INTAKE_REJECTED,
            "The requested revision is not superseded, so the stale-revision scenario does not apply.",
            task,
            registry,
            decisions,
            started,
        )

    if task.scenario == "conflicting_evidence":
        specification = registry.current("SPEC-079200")
        submittal = registry.current("SUBMITTAL-FIRESTOP")
        if specification is None or submittal is None:
            return _safe_outcome(
                TerminalState.MISSING_SOURCE,
                "The conflict scenario requires the current firestopping specification and current approved submittal.",
                task,
                registry,
                decisions,
                started,
            )
        spec_citation = _citation(specification, "governing requirement")
        submittal_citation = _citation(submittal, "installation note")
        return _safe_outcome(
            TerminalState.CONFLICTING_EVIDENCE,
            "Current approved sources contain materially different firestopping requirements. The runner escalated both citations and made no interpretation.",
            task,
            registry,
            decisions,
            started,
            warnings=[
                f"Conflict source A: {spec_citation.document_id} r{spec_citation.revision} — {spec_citation.source_text}",
                f"Conflict source B: {submittal_citation.document_id} r{submittal_citation.revision} — {submittal_citation.source_text}",
            ],
        )

    if task.scenario != "supported_evidence":
        return _safe_outcome(
            TerminalState.INTAKE_REJECTED,
            f"Unknown evaluation scenario: {task.scenario}",
            task,
            registry,
            decisions,
            started,
        )

    drawing = registry.current("A-101")
    specification = registry.current("SPEC-079200")
    if drawing is None or specification is None:
        return _safe_outcome(
            TerminalState.MISSING_SOURCE,
            "The supported-evidence scenario requires the current A-101 drawing and current firestopping specification.",
            task,
            registry,
            decisions,
            started,
        )
    drawing_citation = _citation(drawing, "detail D7")
    specification_citation = _citation(specification, "governing requirement")
    claims = [
        EvidenceClaim(
            claim_id="C-001",
            claim_type="drawing_detail",
            text=f"Verified current drawing evidence: {drawing_citation.source_text}",
            citations=(drawing_citation,),
        ),
        EvidenceClaim(
            claim_id="C-002",
            claim_type="specification_requirement",
            text=f"Verified current specification evidence: {specification_citation.source_text}",
            citations=(specification_citation,),
        ),
    ]
    if len(claims) > task.max_output_claims:
        return _safe_outcome(
            TerminalState.POLICY_BLOCKED,
            "The generated evidence packet would exceed the manifest output-claim budget.",
            task,
            registry,
            decisions,
            started,
        )
    verification = verify_claims(claims, registry)
    failed = [finding for finding in verification if not finding.valid]
    if failed:
        return _safe_outcome(
            TerminalState.VERIFICATION_FAILED,
            "The runner rejected the proposed evidence packet because one or more claims could not be replayed against a current approved source.",
            task,
            registry,
            decisions,
            started,
            warnings=[finding.reason for finding in failed],
        )
    return EvidenceOutcome(
        terminal_state=TerminalState.EVIDENCE_PACKET_READY,
        summary="Current drawing and specification sources were cited and replay-validated. A human project manager must still determine any official RFI response.",
        task=task,
        registry=registry.snapshot(),
        claims=claims,
        policy_events=decisions,
        elapsed_seconds=round(perf_counter() - started, 6),
    )
