"""Strict local JSON intake for evaluation-alpha RFI tasks and document bundles."""

from __future__ import annotations

import json
from pathlib import Path

from .models import ProjectDocument, SourceRegion, TaskSpec


class IntakeError(ValueError):
    """Raised when a local manifest or fixture bundle is malformed."""


_TASK_FIELDS = {
    "task_id",
    "rfi_id",
    "question",
    "bundle_path",
    "allowed_document_keys",
    "required_document_keys",
    "scenario",
    "requested_revision",
    "max_documents",
    "max_output_claims",
}


def load_task(path: Path) -> TaskSpec:
    """Load one versioned local task without accepting undeclared fields."""

    data = json.loads(path.read_text(encoding="utf-8"))
    unknown = set(data) - _TASK_FIELDS
    missing = {"task_id", "rfi_id", "question", "bundle_path", "allowed_document_keys", "required_document_keys", "scenario"} - set(data)
    if unknown:
        raise IntakeError(f"Unknown task fields: {', '.join(sorted(unknown))}")
    if missing:
        raise IntakeError(f"Missing task fields: {', '.join(sorted(missing))}")
    requested = data.get("requested_revision")
    if requested is not None and (not isinstance(requested, list) or len(requested) != 2 or not isinstance(requested[1], int)):
        raise IntakeError("requested_revision must be [document_key, integer_revision] when supplied")
    allowed = tuple(str(value) for value in data["allowed_document_keys"])
    required = tuple(str(value) for value in data["required_document_keys"])
    if not allowed or not required:
        raise IntakeError("allowed_document_keys and required_document_keys must not be empty")
    if not set(required).issubset(allowed):
        raise IntakeError("required_document_keys must be a subset of allowed_document_keys")
    max_documents = int(data.get("max_documents", 20))
    max_output_claims = int(data.get("max_output_claims", 12))
    if max_documents < 1 or max_output_claims < 1:
        raise IntakeError("manifest budgets must be positive")
    return TaskSpec(
        task_id=str(data["task_id"]),
        rfi_id=str(data["rfi_id"]),
        question=str(data["question"]),
        bundle_path=str(data["bundle_path"]),
        allowed_document_keys=allowed,
        required_document_keys=required,
        scenario=str(data["scenario"]),
        requested_revision=(str(requested[0]), int(requested[1])) if requested else None,
        max_documents=max_documents,
        max_output_claims=max_output_claims,
    )


def load_bundle(path: Path) -> tuple[ProjectDocument, ...]:
    """Load a local structured fixture bundle with revision/provenance metadata."""

    data = json.loads(path.read_text(encoding="utf-8"))
    documents = data.get("documents")
    if not isinstance(documents, list) or not documents:
        raise IntakeError("bundle must contain a non-empty documents list")
    parsed: list[ProjectDocument] = []
    seen_ids: set[str] = set()
    for item in documents:
        required = {"document_id", "document_key", "revision", "status", "discipline", "title", "regions"}
        if set(item) != required:
            raise IntakeError(f"document {item.get('document_id', '<unknown>')} has missing or unknown fields")
        document_id = str(item["document_id"])
        if document_id in seen_ids:
            raise IntakeError(f"duplicate document_id: {document_id}")
        seen_ids.add(document_id)
        regions = item["regions"]
        if not isinstance(regions, list) or not regions:
            raise IntakeError(f"document {document_id} must contain source regions")
        parsed_regions: list[SourceRegion] = []
        for region in regions:
            if set(region) != {"page_or_sheet", "region_label", "text", "parser_confidence"}:
                raise IntakeError(f"document {document_id} has malformed source region")
            confidence = float(region["parser_confidence"])
            if not 0.0 <= confidence <= 1.0:
                raise IntakeError(f"document {document_id} has invalid parser confidence")
            parsed_regions.append(
                SourceRegion(
                    page_or_sheet=str(region["page_or_sheet"]),
                    region_label=str(region["region_label"]),
                    text=str(region["text"]),
                    parser_confidence=confidence,
                )
            )
        parsed.append(
            ProjectDocument(
                document_id=document_id,
                document_key=str(item["document_key"]),
                revision=int(item["revision"]),
                status=str(item["status"]),
                discipline=str(item["discipline"]),
                title=str(item["title"]),
                regions=tuple(parsed_regions),
            )
        )
    return tuple(parsed)
