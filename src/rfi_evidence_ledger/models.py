"""Domain contracts for the bounded RFI Evidence Ledger evaluation alpha."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TerminalState(str, Enum):
    """Safe terminal states exposed to the human reviewer."""

    EVIDENCE_PACKET_READY = "evidence_packet_ready"
    STALE_REVISION_DETECTED = "stale_revision_detected"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    MISSING_SOURCE = "missing_source"
    POLICY_BLOCKED = "policy_blocked"
    VERIFICATION_FAILED = "verification_failed"
    INTAKE_REJECTED = "intake_rejected"


@dataclass(frozen=True)
class SourceRegion:
    """A provenance-preserving text region inside an approved local document."""

    page_or_sheet: str
    region_label: str
    text: str
    parser_confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProjectDocument:
    """A small structured document representation used by the offline alpha fixture."""

    document_id: str
    document_key: str
    revision: int
    status: str
    discipline: str
    title: str
    regions: tuple[SourceRegion, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "document_key": self.document_key,
            "revision": self.revision,
            "status": self.status,
            "discipline": self.discipline,
            "title": self.title,
            "regions": [region.to_dict() for region in self.regions],
        }


@dataclass(frozen=True)
class TaskSpec:
    """Human authorization to inspect one RFI using one explicit document bundle."""

    task_id: str
    rfi_id: str
    question: str
    bundle_path: str
    allowed_document_keys: tuple[str, ...]
    required_document_keys: tuple[str, ...]
    scenario: str
    requested_revision: tuple[str, int] | None = None
    max_documents: int = 20
    max_output_claims: int = 12

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "rfi_id": self.rfi_id,
            "question": self.question,
            "bundle_path": self.bundle_path,
            "allowed_document_keys": list(self.allowed_document_keys),
            "required_document_keys": list(self.required_document_keys),
            "scenario": self.scenario,
            "requested_revision": list(self.requested_revision) if self.requested_revision else None,
            "max_documents": self.max_documents,
            "max_output_claims": self.max_output_claims,
        }


@dataclass(frozen=True)
class Citation:
    """A claim-level pointer to an approved source region."""

    document_id: str
    document_key: str
    revision: int
    page_or_sheet: str
    region_label: str
    source_text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceClaim:
    """A structured claim whose source citation can be replayed by a verifier."""

    claim_id: str
    claim_type: str
    text: str
    citations: tuple[Citation, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_type": self.claim_type,
            "text": self.text,
            "citations": [citation.to_dict() for citation in self.citations],
        }


@dataclass(frozen=True)
class PolicyDecision:
    """A deterministic authorization verdict made outside any model."""

    allowed: bool
    rule: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourcePreflight:
    """One bounded, local readiness check for an independently authorized source key."""

    document_key: str
    source_present: bool
    allowlisted: bool
    current_document_id: str | None
    current_revision: int | None
    status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceOutcome:
    """All reviewable evidence from one bounded offline investigation."""

    terminal_state: TerminalState
    summary: str
    task: TaskSpec
    registry: dict[str, dict[str, Any]] = field(default_factory=dict)
    claims: list[EvidenceClaim] = field(default_factory=list)
    policy_events: list[PolicyDecision] = field(default_factory=list)
    source_preflight: list[SourcePreflight] = field(default_factory=list)
    dependency_map: list[dict[str, Any]] = field(default_factory=list)
    route_trace: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "terminal_state": self.terminal_state.value,
            "summary": self.summary,
            "task": self.task.to_dict(),
            "registry": self.registry,
            "claims": [claim.to_dict() for claim in self.claims],
            "policy_events": [event.to_dict() for event in self.policy_events],
            "source_preflight": [check.to_dict() for check in self.source_preflight],
            "dependency_map": self.dependency_map,
            "route_trace": self.route_trace,
            "warnings": self.warnings,
            "elapsed_seconds": self.elapsed_seconds,
        }
