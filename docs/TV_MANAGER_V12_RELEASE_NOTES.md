# TV Manager v12 — Development Release Notes

## 12.0.0-dev.3

This increment adds the first persistent runtime path and operational search orchestration.

### Added

- Native SQLite-backed v12 show repository with explicit schema ownership and typed serialization of shows and episodes.
- Compatibility wrappers for legacy/provider callables behind stable provider/downloader adapter contracts.
- Search orchestration with provider health checks, provider fan-out, candidate aggregation, deterministic decision selection, optional automatic downloader submission, and an in-process decision journal.
- Queue/activity state model with progress reconciliation, unknown-client recovery, bounded history, and explicit removal events.
- Regression tests covering persistent repository round-trip behavior, automatic search/submission, and queue recovery.

### Safety and migration

- The new SQLite repository is separate from the legacy SickChill database; dev.3 does not mutate legacy tables.
- Legacy integrations can be introduced through compatibility wrappers while v12 service contracts remain stable.
- Search provider failures are contained at adapter/orchestration boundaries so one unhealthy source does not terminate a complete search run.

### Next

Persist jobs/search history/queue state, complete legacy schema reconciliation into native v12 storage, add concrete Newznab/Torznab and downloader adapters, expose the runtime through a versioned API, and introduce restart-safe background scheduling.

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
