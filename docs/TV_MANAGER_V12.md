# TV Manager v12 Modernization Baseline

TV Manager v12 is the modernization track for this repository. The objective is not to merely reskin SickChill, but to evolve it into a reliable, migration-safe, API-first television automation platform with clearer configuration, stronger diagnostics, better search intelligence, and a modern responsive interface.

## v12 principles

1. **Migration safety first.** Existing SickChill users must be able to preserve shows, episodes, statuses, quality settings, history, provider configuration, download clients, post-processing behavior, and library state. Migration tooling is read-only against the source database and produces an inspectable manifest before any cutover.
2. **Additive modernization.** New v12 modules live beside legacy runtime code until parity is proven. This avoids destabilizing a working installation while services are extracted.
3. **API-first boundaries.** Core domain logic should not depend on templates or web handlers. Search, download, post-processing, notifications, metadata, migration, and diagnostics should expose stable service boundaries suitable for REST and future event-driven clients.
4. **Deterministic search decisions.** Candidate selection must explain why a result was accepted, rejected, or preferred. Quality, required/rejected words, provider health, release traits, seeders/age, failed history, and user overrides should be represented in a score/explanation model.
5. **Operational visibility.** Provider failures, downloader errors, post-processing failures, metadata/indexer issues, scheduler lag, migration warnings, and database health must be visible without reading raw logs.
6. **Extensibility without hidden coupling.** Providers, download clients, metadata sources, notifications, and post-processors should move toward typed adapters with capability declarations and health checks.

## v12 foundation included in this branch

- `tvmanager_v12.domain` introduces typed, framework-independent models for shows, episodes, episode status, quality profiles, and download candidates.
- Candidate scoring supports quality acceptance, preferred quality ranking, required words, rejected words, seeder contribution, and provider-specific score adjustments.
- `tvmanager_v12.migration` opens the legacy SQLite database in **read-only mode**, exports migration-relevant tables, preserves unknown fields, reports missing/unhandled tables, captures `PRAGMA user_version`, and can include the legacy INI configuration.
- `tools/tvmanager_v12_migrate.py` provides a command-line migration snapshot tool.
- Tests cover domain scoring, missing-episode tracking, and preservation of legacy database records.

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

## Recommended next implementation sequence

1. Complete migration mapping for every legacy table/config section and produce validation reports.
2. Add a compatibility repository/service layer around existing SickChill data access.
3. Introduce a stable v12 service API for library, episodes, search, queue, history, settings, and diagnostics.
4. Move provider/downloader logic behind typed adapters and add health/capability reporting.
5. Build the new web client against the service API while retaining the legacy UI during parity work.
6. Add migration cutover/rollback tooling and parity regression suites.
7. Promote v12 from additive modules to the default runtime only after functional parity is measured.

## Version

Foundation version: **12.0.0-dev.1**

This is an implementation baseline, not a claim of full SickChill parity yet. Each subsequent v12 increment should keep the repository documentation and migration compatibility matrix current.
