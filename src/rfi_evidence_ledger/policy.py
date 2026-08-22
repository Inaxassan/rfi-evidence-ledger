"""Policy-as-code for the local evaluation alpha."""

from __future__ import annotations

from .models import PolicyDecision, ProjectDocument, TaskSpec


def evaluate_bundle_policy(task: TaskSpec, documents: tuple[ProjectDocument, ...]) -> list[PolicyDecision]:
    """Return audit-friendly decisions for manifest and bundle compatibility."""

    decisions: list[PolicyDecision] = []
    bundle_keys = {document.document_key for document in documents}
    unknown_keys = bundle_keys - set(task.allowed_document_keys)
    if unknown_keys:
        decisions.append(
            PolicyDecision(
                allowed=False,
                rule="manifest.document_allowlist",
                reason=f"Bundle contains unauthorized document keys: {', '.join(sorted(unknown_keys))}",
            )
        )
    else:
        decisions.append(
            PolicyDecision(
                allowed=True,
                rule="manifest.document_allowlist",
                reason="All bundle document keys are explicitly authorized by the task manifest.",
            )
        )
    missing_required = set(task.required_document_keys) - bundle_keys
    if missing_required:
        decisions.append(
            PolicyDecision(
                allowed=False,
                rule="manifest.required_evidence",
                reason=f"Required document keys are missing: {', '.join(sorted(missing_required))}",
            )
        )
    else:
        decisions.append(
            PolicyDecision(
                allowed=True,
                rule="manifest.required_evidence",
                reason="All required evidence document keys are present in the authorized bundle.",
            )
        )
    if len(documents) > task.max_documents:
        decisions.append(
            PolicyDecision(
                allowed=False,
                rule="budget.max_documents",
                reason=f"Bundle contains {len(documents)} documents; manifest permits {task.max_documents}.",
            )
        )
    else:
        decisions.append(
            PolicyDecision(
                allowed=True,
                rule="budget.max_documents",
                reason=f"Bundle contains {len(documents)} documents within the manifest budget.",
            )
        )
    return decisions


def policy_allows(decisions: list[PolicyDecision]) -> bool:
    """A single rejected policy decision fails the run closed."""

    return all(decision.allowed for decision in decisions)
