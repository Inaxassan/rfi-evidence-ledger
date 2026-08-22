"""A small offline runner for deterministic construction-document evidence evaluation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from .models import Citation, EvidenceClaim, EvidenceOutcome, ProjectDocument, SourcePreflight, TaskSpec, TerminalState
from .policy import evaluate_bundle_policy, policy_allows
from .registry import RevisionRegistry
from .verifier import verify_claims


_DEPENDENCY_MAP = (
    {
        "step": "intake",
        "depends_on": [],
        "purpose": "Load one approved task manifest and one local versioned bundle.",
    },
    {
        "step": "policy_preflight",
        "depends_on": ["intake"],
        "purpose": "Fail closed on bundle allowlist, required-evidence, and document-budget violations.",
    },
    {
        "step": "source_preflight_fan",
        "depends_on": ["intake"],
        "purpose": "Check each independent required source key locally, then join results in sorted manifest order.",
    },
    {
        "step": "scenario_evidence",
        "depends_on": ["policy_preflight", "source_preflight_fan"],
        "purpose": "Construct only the bounded scenario evidence permitted by the manifest.",
    },
    {
        "step": "citation_replay",
        "depends_on": ["scenario_evidence"],
        "purpose": "Replay every citation against the current approved source registry.",
    },
    {
        "step": "human_review",
        "depends_on": ["citation_replay"],
        "purpose": "Require a human project decision; the alpha cannot issue or change an RFI.",
    },
)

_MAX_PREFLIGHT_WORKERS = 4


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
    source_preflight: list[SourcePreflight] | None = None,
    route: str = "safe_stop",
    route_reason: str = "The runner reached a deterministic safe-stop state.",
) -> EvidenceOutcome:
    return EvidenceOutcome(
        terminal_state=state,
        summary=summary,
        task=task,
        registry=registry.snapshot(),
        policy_events=list(decisions),
        source_preflight=source_preflight or [],
        dependency_map=list(_DEPENDENCY_MAP),
        route_trace=[{"route": route, "reason": route_reason}],
        warnings=warnings or [],
        elapsed_seconds=round(perf_counter() - started, 6),
    )


def _preflight_source(task: TaskSpec, documents: tuple[ProjectDocument, ...], registry: RevisionRegistry, key: str) -> SourcePreflight:
    """Check one required source key without reading or modifying any external system."""

    present = any(document.document_key == key for document in documents)
    allowlisted = key in task.allowed_document_keys
    current = registry.current(key)
    if not allowlisted:
        return SourcePreflight(key, present, False, None, None, "blocked", "The source key is outside the task allowlist.")
    if not present:
        return SourcePreflight(key, False, True, None, None, "missing", "The required source key is absent from the local bundle.")
    if current is None:
        return SourcePreflight(key, True, True, None, None, "no_current_revision", "No current approved revision is available for this source key.")
    return SourcePreflight(
        key,
        True,
        True,
        current.document_id,
        current.revision,
        "ready",
        "A current approved revision is available in the authorized local bundle.",
    )


def _run_source_preflight(task: TaskSpec, documents: tuple[ProjectDocument, ...], registry: RevisionRegistry) -> list[SourcePreflight]:
    """Run independent required-source checks concurrently and return a deterministic sorted join."""

    keys = tuple(sorted(set(task.required_document_keys)))
    if not keys:
        return []
    workers = min(_MAX_PREFLIGHT_WORKERS, len(keys))
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="rfi-source-preflight") as executor:
        futures = {key: executor.submit(_preflight_source, task, documents, registry, key) for key in keys}
        return [futures[key].result() for key in keys]


def run(task: TaskSpec, documents: tuple[ProjectDocument, ...]) -> EvidenceOutcome:
    """Run one deterministic evaluation-alpha task without model calls or network access."""

    started = perf_counter()
    registry = RevisionRegistry(documents)
    decisions = evaluate_bundle_policy(task, documents)
    source_preflight = _run_source_preflight(task, documents, registry)
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
            source_preflight=source_preflight,
            route="policy_stop",
            route_reason="The manifest boundary or document budget was not satisfied before evidence generation.",
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
                source_preflight=source_preflight,
                route="intake_stop",
                route_reason="The stale-revision scenario omitted its required requested revision.",
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
                source_preflight=source_preflight,
                route="missing_source_stop",
                route_reason="The requested revision was not present in the authorized local bundle.",
            )
        if current is not None and not registry.is_current(requested):
            return _safe_outcome(
                TerminalState.STALE_REVISION_DETECTED,
                f"{requested.document_id} revision {requested.revision} is superseded by {current.document_id} revision {current.revision}; the runner will not use it as governing evidence.",
                task,
                registry,
                decisions,
                started,
                source_preflight=source_preflight,
                route="stale_revision_stop",
                route_reason="The requested source is superseded and cannot govern evidence.",
            )
        return _safe_outcome(
            TerminalState.INTAKE_REJECTED,
            "The requested revision is not superseded, so the stale-revision scenario does not apply.",
            task,
            registry,
            decisions,
            started,
            source_preflight=source_preflight,
            route="intake_stop",
            route_reason="The requested revision is not superseded, so the stale-revision evaluation path does not apply.",
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
                source_preflight=source_preflight,
                route="missing_source_stop",
                route_reason="One or more conflict sources are missing from the authorized local bundle.",
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
            source_preflight=source_preflight,
            route="conflict_stop",
            route_reason="Current approved sources disagree and the runner will not interpret the conflict.",
        )

    if task.scenario != "supported_evidence":
        return _safe_outcome(
            TerminalState.INTAKE_REJECTED,
            f"Unknown evaluation scenario: {task.scenario}",
            task,
            registry,
            decisions,
            started,
            source_preflight=source_preflight,
            route="intake_stop",
            route_reason="The requested evaluation scenario is not recognized by this alpha.",
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
            source_preflight=source_preflight,
            route="missing_source_stop",
            route_reason="A required supported-evidence source lacks a current approved revision.",
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
            source_preflight=source_preflight,
            route="claim_budget_stop",
            route_reason="The proposed evidence packet exceeds the manifest claim budget.",
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
            source_preflight=source_preflight,
            route="verification_stop",
            route_reason="One or more citations could not be replayed against current approved sources.",
        )
    return EvidenceOutcome(
        terminal_state=TerminalState.EVIDENCE_PACKET_READY,
        summary="Current drawing and specification sources were cited and replay-validated. A human project manager must still determine any official RFI response.",
        task=task,
        registry=registry.snapshot(),
        claims=claims,
        policy_events=decisions,
        source_preflight=source_preflight,
        dependency_map=list(_DEPENDENCY_MAP),
        route_trace=[
            {
                "route": "human_review_required",
                "reason": "All claims replayed against current approved local sources; a human must still decide any project action.",
            }
        ],
        elapsed_seconds=round(perf_counter() - started, 6),
    )
