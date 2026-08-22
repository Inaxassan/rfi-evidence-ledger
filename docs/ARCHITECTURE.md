# Architecture

RFI Evidence Ledger is designed as an **evidence-control layer**. In the evaluation alpha, the source bundle is a transparent local JSON fixture rather than a real PDF/CAD parser or customer connector. The same bounded flow is intended for a future customer-controlled pilot.

```mermaid
flowchart LR
    PM[Project manager selects one RFI] --> M[Strict task manifest]
    M --> P{Policy gateway}
    P -->|authorized local bundle| I[Source ingestion]
    P -->|unknown source / budget breach| S1[policy_blocked]
    I --> R[Revision registry]
    R --> H[Hybrid retrieval design]
    H --> W[Evidence worker]
    W --> V{Independent verifier}
    V -->|citation + current revision valid| D[Evidence dossier + JSON receipt]
    V -->|citation invalid| S2[verification_failed]
    R -->|source superseded| S3[stale_revision_detected]
    R -->|required source absent| S4[missing_source]
    W -->|current sources conflict| S5[conflicting_evidence]
    D --> HR[Human reviewer decides any official action]

    classDef human fill:#F4EBD7,stroke:#D66A2C,color:#172B4D;
    classDef control fill:#172B4D,stroke:#F2B134,color:#F4EBD7;
    classDef stop fill:#FCE7E1,stroke:#B42318,color:#5B1B13;
    class PM,HR human;
    class P,V control;
    class S1,S2,S3,S4,S5 stop;
```

## Alpha implementation versus future pilot design

| Layer | Evaluation alpha | Future customer-controlled pilot |
|---|---|---|
| Source intake | Transparent local JSON fixture. | Customer-approved drawings, specifications, addenda, submittals, and RFI records through a named bundle manifest. |
| Parsing | Fixture source regions include page/sheet labels and parser-confidence fields. | Layout-aware PDF/image/drawing parser that preserves title blocks, revision tables, source page/sheet, bounding regions, and parsing warnings. |
| Revision control | Declared document key/revision/status metadata. | Deterministic source registry backed by customer-approved document-control metadata. |
| Retrieval | Controlled scenario logic. | Revision-filtered metadata, exact lexical references, semantic retrieval, and coverage checks. |
| Evidence claims | Deterministic fixture claims. | Structured claim/citation proposals with no material claim accepted without validated evidence. |
| Verification | Replays citation existence and current revision. | Citation/source-span checks, current-revision validation, conflict/gap detection, policy checks, and optional isolated semantic support review. |
| Output | Markdown dossier and JSON receipt. | Same artifact types plus customer-approved retention, trace export, and human-decision receipt. |
| External actions | None. | Still none by default; any read-only or write integration would require a separate customer security and authorization design. |

## Non-negotiable properties

The source bundle is selected before a run; the policy engine—not a model—enforces which source classes may be read; evidence claims carry citations; citation validation is separate from evidence generation; and a human reviewer makes any project decision. The alpha’s explicit stop states are part of the product behavior, not error messages to ignore.
