# TV Manager v12 — Development Release Notes

## 12.0.0-dev.2

This increment moves v12 from domain/migration primitives into the first reliability and service layer needed for a modern TV automation platform.

### Added

- Typed provider and downloader adapter contracts with normalized request/response models.
- Adapter health model with healthy, degraded, unavailable, and unknown states plus latency and diagnostic text.
- Explainable candidate evaluation with explicit accepted, rejected, and suppressed states.
- Search-reason records that show required-word, rejected-word, quality, seeder, and adjustment effects.
- Deterministic best-candidate selection.
- Failed-download suppression using stable provider/title/protocol fingerprints and configurable expiry.
- Show repository protocol and in-memory reference implementation.
- Library service for show listing, wanted-episode queue generation, episode-state updates, and bulk upsert.
- Regression tests covering search explanations, suppression expiry, paused-show queue behavior, and adapter health timestamps.

### Direction

The next increment will connect these contracts to persistent SickChill-compatible storage and concrete provider/downloader implementations, then expose them through a versioned service API. Search diagnostics and decision history will remain first-class features so the UI can explain not only what was selected, but why alternatives were rejected.

## 12.0.0-dev.1

This development baseline begins the TV Manager modernization track as an additive layer on top of the existing SickChill codebase.

### Added

- New `tvmanager_v12` package for framework-independent domain logic.
- Typed show, episode, episode-status, quality-profile, and download-candidate models.
- Deterministic download candidate scoring with quality, required/rejected words, seeders, and score adjustments.
- Read-only SickChill SQLite migration exporter with table counts, schema version capture, warnings, and optional config capture.
- CLI migration snapshot tool at `tools/tvmanager_v12_migrate.py`.
- Regression tests for scoring, episode-state tracking, and migration row preservation.
- Architecture, capability, migration, and project status documentation for the v12 modernization path.

### Safety

- No legacy runtime behavior is replaced by this release.
- Legacy databases are opened read-only by the migration exporter.
- Unknown or currently-unhandled legacy tables are reported rather than silently discarded.
- Migration design keeps rollback and reconciliation as explicit requirements.
