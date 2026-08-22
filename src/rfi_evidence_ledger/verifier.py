"""Independent deterministic verification for evidence claims."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Citation, EvidenceClaim
from .registry import RevisionRegistry


@dataclass(frozen=True)
class VerificationFinding:
    claim_id: str
    valid: bool
    reason: str


def _citation_exists(citation: Citation, registry: RevisionRegistry) -> bool:
    for document in registry.by_key.get(citation.document_key, []):
        if document.document_id != citation.document_id or document.revision != citation.revision:
            continue
        for region in document.regions:
            if (
                region.page_or_sheet == citation.page_or_sheet
                and region.region_label == citation.region_label
                and region.text == citation.source_text
            ):
                return True
    return False


def verify_claims(claims: list[EvidenceClaim], registry: RevisionRegistry) -> list[VerificationFinding]:
    """Replay citation metadata independently of the evidence worker."""

    findings: list[VerificationFinding] = []
    for claim in claims:
        if not claim.citations:
            findings.append(VerificationFinding(claim.claim_id, False, "Claim has no citations."))
            continue
        for citation in claim.citations:
            if not _citation_exists(citation, registry):
                findings.append(VerificationFinding(claim.claim_id, False, "Citation does not resolve to an approved source region."))
                break
            document = registry.requested(citation.document_key, citation.revision)
            if document is None or not registry.is_current(document):
                findings.append(VerificationFinding(claim.claim_id, False, "Citation refers to a superseded or ambiguous source revision."))
                break
            if citation.source_text.lower() not in claim.text.lower():
                findings.append(VerificationFinding(claim.claim_id, False, "Claim does not carry the exact cited source statement in this deterministic alpha."))
                break
        else:
            findings.append(VerificationFinding(claim.claim_id, True, "Citation exists and references a current approved source region."))
    return findings
