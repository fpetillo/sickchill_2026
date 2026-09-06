# TV Manager v12 Modernization Baseline

TV Manager v12 is the modernization track for this repository. The objective is not to merely reskin SickChill, but to evolve it into a reliable, migration-safe, API-first television automation platform with clearer configuration, stronger diagnostics, better search intelligence, restart-safe operations, and a modern responsive interface.

## v12 principles

1. **Migration safety first.** Existing SickChill users must be able to preserve shows, episodes, statuses, quality settings, history, provider configuration, download clients, post-processing behavior, and library state.
2. **Additive modernization.** New v12 modules live beside legacy runtime code until parity is proven.
3. **API-first boundaries.** Core domain logic must remain independent from templates and web handlers.
4. **Deterministic search decisions.** Candidate selection must explain why results were accepted, rejected, suppressed, or preferred.
5. **Operational visibility.** Provider, downloader, post-processing, metadata, scheduler, migration, and database failures must be visible without raw-log archaeology.
6. **Restart safety.** Queue, search history, and job state must recover from process restarts and stale workers without losing operational context.
7. **Extensibility without hidden coupling.** Providers, downloaders, metadata sources, notifications, and post-processors move behind typed contracts.

## Implemented foundation

### Domain and migration
- Typed framework-independent show, episode, quality, status, and candidate models.
- Download candidates preserve normalized protocol, download URL, and provider GUID.
- Read-only legacy SQLite migration snapshot and optional legacy configuration capture.
- Migration warnings and unknown-table reporting rather than silent data loss.

### Search intelligence
- Deterministic quality/word/seeder/adjustment scoring.
- Explicit accepted, rejected, and failed-release-suppressed decisions.
- Stable failed-release fingerprints with configurable TTL.
- Search orchestration with provider health gating, provider fan-out, candidate aggregation, deterministic selection, automatic submission, and decision journaling.
- Optional persistent recording of complete search/provider/decision/submission history.

### Reliability and adapters
- Typed provider and downloader contracts.
- Normalized adapter health state, latency, and diagnostic text.
- Callable compatibility wrappers so current SickChill/provider/client functions can be moved behind v12 boundaries incrementally.
- Concrete Newznab and Torznab protocol foundations.
- Concrete SABnzbd and qBittorrent client foundations.

### Persistence and activity
- Native v12 SQLite show repository kept separate from the legacy SickChill database.
- Repository/service abstraction for library access and wanted-episode calculation.
- Restart-safe SQLite runtime store for queue state, event history, search decision history, and job metadata.
- Persistent activity facade with queue restoration, progress/state reconciliation, unknown-client recovery, bounded history, and removal events.

### Automation and API
- Persistent scheduler/job store with due times, enabled state, run/failure accounting, crash-safe leases, and stale-lease recovery.
- Versioned `/api/v1` JSON facade for status, library, wanted, queue, history, search history, jobs, due-job execution, and episode-state mutation.
- Dependency-free WSGI entry point with optional bearer-token protection.

## Target v12 capability map

### Library and series management
- Existing-series import and recursive library scan
- Show/season/episode monitoring states
- Specials, multi-episode releases, air-by-date, sports, anime, scene numbering, DVD order
- Root-folder management and safe path moves
- Metadata/artwork refresh with source provenance
- Mass edit, filters, saved views, duplicate detection, and library repair

### Search and acquisition
- Scheduled backlog/recent search and interactive manual search
- Newznab/Torznab plus native provider adapters
- Provider capability/health testing, rate-limit awareness, retry/backoff, and circuit breakers
- Quality profiles and custom release traits
- Failed-download memory, duplicate suppression, persisted decision history, and explainable ranking
- NZB/torrent client integrations with queue reconciliation

### Post-processing
- Completed-download handling and manual processing
- Rename/move/copy/hardlink strategies
- Reprocessing/repair workflows
- Multi-file and multi-episode handling
- Subtitle acquisition and forced/foreign preferences
- Metadata/NFO/artwork generation
- Idempotent processing so retries do not corrupt a library

### Automation and operations
- Restart-safe scheduler with visible jobs, progress, retry state, cancellation, leases, and concurrency limits
- Structured persistent event/history stream
- Health dashboard for indexers, providers, downloaders, filesystem access, database, and jobs
- Backup/restore and pre-upgrade snapshots
- Safe migration preview, dry run, validation, cutover, and rollback
- Docker and native deployment paths

### Modern interface
- Responsive dashboard focused on actionable exceptions
- Show grid/table views, season drill-down, episode timeline and search history
- Unified activity/queue/history views
- Interactive search with decision explanations
- Configuration grouped by user intent rather than legacy implementation detail
- Inline diagnostics, connection tests, setup validation, accessibility, themes, and mobile layouts

## Recommended next implementation sequence

1. Finish complete legacy SickChill schema/config mapping and reconciliation into native v12 storage.
2. Persist failed-release suppression plus provider/downloader health and retry/circuit-breaker state.
3. Add SABnzbd/qBittorrent queue polling and reconcile completed/failed items into processing jobs.
4. Build idempotent post-processing planning/journaling and completed-download handling.
5. Expand `/api/v1` for interactive search, provider/client tests, diagnostics, settings, backup/restore, migration and processing.
6. Add a machine-readable OpenAPI contract and stronger deployment authentication/secret handling.
7. Build the new responsive client only against the versioned API.
8. Add migration cutover/rollback tooling and full parity regression suites.
9. Promote v12 to the default runtime only after measured parity.

## Version

Current development version: **12.0.0-dev.4**

This is an implementation track, not yet a claim of full SickChill parity.
