# TV Manager v12 Parity Matrix

This matrix tracks functional replacement readiness. A capability is not considered complete merely because a screen or endpoint exists; migration fidelity, failure handling, diagnostics, tests, and rollback impact are part of parity.

| Capability | Legacy baseline | v12 state | Acceptance requirement |
| --- | --- | --- | --- |
| Show / episode domain model | Available | Foundation implemented | Preserve identifiers, statuses, numbering modes, paths, and flags |
| Quality profiles and release scoring | Available | Foundation implemented | Preserve legacy quality intent and add deterministic/explainable selection |
| Required / rejected release words | Available | Implemented | Candidate decisions must explain matching rule outcomes |
| Failed download handling | Available | Suppression primitive implemented | Persist failures, expire/safely release suppression, support manual retry |
| Provider integrations | Available | Typed adapter contract implemented | Concrete providers, health, capabilities, rate limits, retry/backoff |
| Downloader integrations | Available | Typed adapter contract implemented | Concrete clients, health, submit/delete, queue/history normalization |
| Provider/downloader health diagnostics | Limited / log-oriented | Health model implemented | Dashboard-ready health, latency, recent errors, actionable remediation |
| Library repository/service boundary | Legacy direct access | Contract + reference repository implemented | SQLite compatibility repository with transactional behavior and tests |
| Wanted/missing queue calculation | Available | Service primitive implemented | Match legacy monitoring semantics including paused/ignored/special cases |
| Search-decision explanations | Limited | Implemented as first-class model | Persist and expose reasons for accepted/rejected/suppressed candidates |
| Search orchestration | Available | Planned | Provider fan-out, dedupe, ranking, timeout policy, diagnostics, manual search |
| Queue/history | Available | Planned | Normalized multi-client queue/history, intervention, retry, failure recovery |
| Post-processing | Available | Planned | Idempotent processing, rename/move/link, multi-episode, repair workflows |
| Subtitle automation | Available | Planned | Match existing providers/preferences including forced/foreign-only behavior |
| Metadata/artwork | Available | Planned | Source provenance, refresh, conflict handling, repair, filesystem safety |
| Legacy DB/config migration | Available as existing state | Read-only exporter implemented | Complete mapping + validation report + dry run + backup + rollback |
| Versioned service API | Limited legacy API | Planned | Library, episodes, search, queue, history, config, diagnostics |
| Modern responsive UI | Legacy UI | Planned | Feature-complete API-driven workflows, mobile/desktop, accessibility |
| Cutover / rollback | Manual | Planned | Automated backup, reversible cutover, reconciliation, parity regression |

## Release gate

v12 becomes eligible to replace the legacy runtime only after the matrix is substantially complete and automated parity checks cover migrated libraries, critical search/download workflows, post-processing, configuration, and rollback.
