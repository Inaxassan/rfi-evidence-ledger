"""Revision-aware source registry for local, manifest-authorized documents."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import ProjectDocument


class RevisionRegistry:
    """Indexes a fixed source bundle and exposes revision state without model judgment."""

    def __init__(self, documents: tuple[ProjectDocument, ...]) -> None:
        self.documents = documents
        self.by_key: dict[str, list[ProjectDocument]] = defaultdict(list)
        for document in documents:
            self.by_key[document.document_key].append(document)
        for document_list in self.by_key.values():
            document_list.sort(key=lambda item: item.revision)

    def current(self, document_key: str) -> ProjectDocument | None:
        """Return the highest revision explicitly marked current, if exactly one exists."""

        candidates = [document for document in self.by_key.get(document_key, []) if document.status == "current"]
        if len(candidates) != 1:
            return None
        return candidates[0]

    def requested(self, document_key: str, revision: int) -> ProjectDocument | None:
        """Return one exact revision, regardless of current/superseded status."""

        for document in self.by_key.get(document_key, []):
            if document.revision == revision:
                return document
        return None

    def is_current(self, document: ProjectDocument) -> bool:
        current = self.current(document.document_key)
        return current is not None and current.document_id == document.document_id

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Create a reviewer-readable revision ledger for artifacts and receipts."""

        snapshot: dict[str, dict[str, Any]] = {}
        for key, documents in sorted(self.by_key.items()):
            current = self.current(key)
            snapshot[key] = {
                "current_document_id": current.document_id if current else None,
                "current_revision": current.revision if current else None,
                "documents": [
                    {
                        "document_id": document.document_id,
                        "revision": document.revision,
                        "status": document.status,
                        "title": document.title,
                    }
                    for document in documents
                ],
            }
        return snapshot
