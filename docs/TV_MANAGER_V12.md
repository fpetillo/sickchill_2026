# TV Manager v12 Modernization Baseline

TV Manager v12 is the modernization track for this repository. The objective is not to merely reskin SickChill, but to evolve it into a reliable, migration-safe, API-first television automation platform with clearer configuration, stronger diagnostics, better search intelligence, and a modern responsive interface.

## v12 principles

1. **Migration safety first.** Existing SickChill users must be able to preserve shows, episodes, statuses, quality settings, history, provider configuration, download clients, post-processing behavior, and library state. Migration tooling is read-only against the source database and produces an inspectable manifest before any cutover.
2. **Additive modernization.** New v12 modules live beside legacy runtime code until parity is proven. This avoids destabilizing a working installation while services are extracted.
3. **API-first boundaries.** Core domain logic should not depend on templates or web handlers. Search, download, post-processing, notifications, metadata, migration, and diagnostics should expose stable service boundaries suitable for REST and future event-driven clients.
4. **Deterministic and explainable search decisions.** Candidate selection records why a result was accepted, rejected, suppressed, or preferred. Quality, required/rejected words, release traits, seeders, failed history, and score adjustments are represented explicitly.
5. **Operational visibility.** Provider failures, downloader errors, post-processing failures, metadata/indexer issues, scheduler lag, migration warnings, and database health must be visible without reading raw logs.
6. **Extensibility without hidden coupling.** Providers, download clients, metadata sources, notifications, and post-processors move toward typed adapters with capability declarations and health checks.
7. **UI decoupled from runtime internals.** The modern web interface will consume a versioned service API rather than depending directly on legacy web handlers.

## Implemented foundation

### 12.0.0-dev.1

- `tvmanager_v12.domain` introduced typed, framework-independent models for shows, episodes, episode status, quality profiles, and download candidates.
- Candidate scoring added quality acceptance, preferred quality ranking, required words, rejected words, seeder contribution, and provider-specific score adjustments.
- `tvmanager_v12.migration` opens the legacy SQLite database in **read-only mode**, exports migration-relevant tables, preserves unknown fields, reports missing/unhandled tables, captures `PRAGMA user_version`, and can include legacy INI configuration.
- `tools/tvmanager_v12_migrate.py` provides a command-line migration snapshot tool.
- Tests cover domain scoring, missing-episode tracking, and preservation of legacy database records.

### 12.0.0-dev.2

- Added typed `ProviderAdapter` and `DownloaderAdapter` contracts.
- Added normalized search, submission, and health models so integrations can expose consistent behavior.
- Added `SearchDecision`, `CandidateDecision`, and `SearchReason` models so every release can explain why it was accepted, rejected, or suppressed.
- Added deterministic candidate selection on top of quality, required/rejected words, seeders, and score adjustments.
- Added time-bounded failed-release suppression with stable fingerprints to avoid repeatedly grabbing known bad releases.
- Added a `ShowRepository` abstraction plus an in-memory reference repository and `LibraryService` for list, wanted, status update, and bulk-upsert workflows.
- Added regression tests for adapter health, explainable search decisions, suppression expiry, and paused-show queue behavior.

## Target v12 capability map

### Library and series management
- Existing-series import and recursive library scan
- Show/season/episode monitoring states
- Specials, multi-episode releases, air-by-date, sports, anime, scene numbering, DVD order
- Root-folder management and safe path moves
- Metadata/artwork refresh with source provenance
- Mass edit, filters, saved views, duplicate detection, and library repair

### Search and acquisition
- Scheduled backlog and recent search
- Manual and interactive search
- Newznab/Torznab plus native provider adapters
- Provider capability/health testing, rate-limit awareness, retry/backoff, and circuit breakers
- Quality profiles, custom formats/release traits, required/rejected/preferred words
- Failed-download memory, duplicate suppression, and explainable ranking
- Persisted search decision history so the UI can show exactly why one result won over another
- NZB/torrent client integrations with category/label support

### Post-processing
- Completed-download handling and manual processing
- Rename/move/copy/hardlink strategies
- Reprocessing/repair workflows
- Multi-file and multi-episode handling
- Subtitle acquisition and forced/foreign preferences
- Metadata/NFO/artwork generation
- Idempotent processing so retries do not corrupt a library

### Automation and operations
- Scheduler visibility and per-job controls
- Structured event/history stream
- Health dashboard for indexers, providers, downloaders, filesystem access, DB, and background jobs
- Backup/restore and pre-upgrade snapshots
- Safe migration preview, dry run, validation, cutover, and rollback
- Docker and native deployment paths

### Modern interface
- Responsive dashboard focused on actionable exceptions
- Show grid/table views, season drill-down, episode timeline and search history
- Unified activity/queue/history views
- Configuration grouped by intent rather than legacy implementation detail
- Inline diagnostics, connection tests, and setup validation
- Accessibility, keyboard navigation, dark/light themes, and mobile layouts

## Next implementation sequence

1. Complete legacy schema/config mapping and generate a migration validation report with mapped, transformed, preserved, and unresolved fields.
2. Add a SQLite-backed compatibility repository behind the new repository/service interfaces.
3. Add concrete provider/downloader adapter wrappers with health checks, capability metadata, retry/backoff, and rate limiting.
4. Build search orchestration with provider fan-out, deduplication, decision history, and failed-download recovery.
5. Expose versioned service endpoints for library, episodes, search, queue, history, settings, and diagnostics.
6. Build the new web client exclusively against the service API while retaining the legacy UI during parity work.
7. Add migration cutover/rollback tooling and parity regression suites.
8. Promote v12 from additive modules to the default runtime only after functional parity is measured.

## Version

Current development version: **12.0.0-dev.2**

This is an implementation baseline, not a claim of full SickChill parity yet. Each subsequent v12 increment should keep the repository documentation, migration compatibility matrix, tests, and release notes current.
