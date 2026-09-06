# TV Manager v12 Status

Current development version: **12.0.0-dev.2**

This branch establishes the additive v12 modernization foundation without changing the legacy SickChill runtime path.

## Implemented

### 12.0.0-dev.1 foundation

- Typed framework-independent domain objects for shows, episodes, episode states, quality profiles, and download candidates.
- Deterministic candidate scoring with quality acceptance, preferred quality ranking, required words, rejected words, seeders, and score adjustments.
- Read-only legacy SQLite migration exporter.
- Optional legacy INI configuration capture.
- Migration manifest counts, warnings, unknown-table reporting, and SQLite schema version capture.
- CLI migration snapshot tool.
- Regression tests for scoring, episode tracking, and legacy-row preservation.
- v12 architecture/capability roadmap and migration workflow documentation.

### 12.0.0-dev.2 reliability and service layer

- Typed provider and downloader adapter contracts.
- Standard adapter health model with healthy, degraded, unavailable, and unknown states.
- Normalized provider search and downloader submission request/response contracts.
- Explainable search-decision engine that records why each candidate was accepted, rejected, or suppressed.
- Deterministic candidate selection with quality, word rules, seeders, and score adjustments.
- Time-bounded failed-release suppression using stable fingerprints to prevent repeated bad grabs.
- Repository abstraction for shows plus an in-memory reference implementation.
- Library service for show listing, wanted-episode calculation, episode state updates, and bulk upsert.
- Regression coverage for adapter health, search explanations, failed-release expiry, and paused-show queue behavior.
- Architecture, parity, release-note, and capability documentation updated to match the implementation.

## Next code milestones

- Full legacy schema/config mapping and migration validation report.
- SQLite-backed compatibility repository around current SickChill data with transactional writes isolated behind the repository contract.
- Concrete provider adapters and downloader adapters with capability metadata, health checks, retry/backoff, and rate limiting.
- Search orchestration service with provider fan-out, deduplication, diagnostics, and persisted decision history.
- Queue/history services with failed-download recovery and manual intervention controls.
- Versioned service API for library, episodes, search, queue, history, configuration, and diagnostics.
- Modern responsive web interface developed exclusively against the service API.
- Cutover, rollback, backup, and parity regression tooling.

The legacy application remains the operational baseline until parity checks demonstrate that v12 can replace it safely.
