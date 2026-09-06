# TV Manager v12 — Development Release Notes

## 12.0.0-dev.4

This increment turns the v12 branch into a restart-safe service platform that can retain operational state, run scheduled work safely, communicate with standard indexer/download protocols, and expose core capabilities through a versioned JSON API.

### Added

- `SQLiteRuntimeStore` for persistent queue state, event/history records, search decision history, and runtime metadata.
- `PersistentActivityStore` with queue restoration after restart, transactional queue updates, unknown-client recovery, and bounded persistent history.
- `SQLiteJobStore` and `SchedulerEngine` with persistent due times, enable/disable state, crash-safe leases, expired-lease recovery, per-run success/failure state, and failure counters.
- Concrete `NewznabProviderAdapter` and `TorznabProviderAdapter` implementations using standard capabilities and TV-search endpoints.
- Normalized RSS/Newznab parsing for title, size, seeders, download URL, and release GUID.
- Download candidates now retain `download_url` and `guid` fields so accepted results can be submitted without reaching back into provider-specific objects.
- Concrete `SABnzbdAdapter` and `QBittorrentAdapter` foundations with health/version checks, submission, category handling, pause behavior, and delete support.
- Search orchestration hooks for persistent decision recording and queue/activity creation after successful automatic submission.
- `TVManagerAPI` plus a dependency-free WSGI entry point with versioned `/api/v1` routes for status, library, wanted episodes, queue, history, search history, jobs, due-job execution, and episode-status updates.
- Optional bearer-token protection for the WSGI API.
- Phase-4 regression tests for queue persistence, search persistence, scheduler restart/failure behavior, lease recovery, Newznab parsing, and API operations.

### Reliability and safety

- Runtime and scheduler state live in v12-owned SQLite tables; the legacy SickChill database remains untouched by the new runtime path.
- Scheduler leases prevent the same due job from being claimed twice and automatically expire after a crash or stalled worker.
- Provider failures remain isolated at the adapter boundary; one unhealthy provider does not stop the rest of a search run.
- API mutation is currently limited to explicit v12 service operations and does not bypass repository/service boundaries.
- Secrets remain constructor/config inputs to adapters and are not written into queue/search history payloads by the new runtime store.

### Next

Complete full legacy-schema reconciliation, persist failed-release suppression, add downloader queue polling and completed-download processing jobs, strengthen provider/client retry and circuit-breaker behavior, expand diagnostics/settings/manual-search API coverage, publish an OpenAPI contract, and begin the new responsive web interface against `/api/v1`.

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
