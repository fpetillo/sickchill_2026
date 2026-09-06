# TV Manager v12 Architecture Direction

## Runtime shape

TV Manager v12 is evolving toward a layered architecture that separates core decisions from transport and presentation concerns:

- **Domain** — shows, episodes, monitoring, quality, release traits, scoring, policies.
- **Application services** — library, search, queue, post-processing, migration, history, diagnostics, settings.
- **Adapters** — indexers, search providers, download clients, metadata/artwork, subtitles, notifications, filesystem.
- **Persistence** — legacy compatibility repositories during transition, followed by explicit v12 persistence models/migrations.
- **API** — versioned service endpoints and events; UI never reaches directly into database or legacy globals.
- **Web UI** — responsive client focused on library state, exceptions, queue/activity, search decisions, diagnostics, and configuration.

## Transition strategy

The current SickChill runtime remains intact while v12 services are introduced beside it. New code should avoid depending on global runtime state whenever possible. Compatibility adapters can translate legacy objects/configuration into v12 domain objects until native v12 persistence is ready.

## Service boundaries

### LibraryService
Owns show/episode inventory, monitoring state, root folders, scans, imports, moves, metadata refresh, and repair operations. The first repository contract and in-memory reference service are now implemented.

### SearchService
Owns recent/backlog/manual search orchestration, provider capability filtering, candidate normalization, scoring, rejection reasons, deduplication, failed-history checks, and dispatch decisions. v12 now has first-class candidate decision/reason models and failed-release suppression primitives.

### DownloadService
Owns downloader capabilities, connection tests, queue submission, status mapping, category/label handling, and download reconciliation. Typed downloader request/submission contracts now define the integration boundary.

### ProcessingService
Owns completed-download matching, rename/move/copy/hardlink planning, subtitle and metadata sidecars, idempotency, operation journaling, and repair/reprocess actions.

### MigrationService
Owns legacy inspection, mapping, preview, validation, import, cutover, and rollback metadata. It must never silently drop unknown legacy values.

### DiagnosticsService
Owns health/readiness state for database, filesystem, scheduler, metadata/indexers, providers, download clients, background jobs, and migration blockers. v12 adapters now share a normalized health state and latency/diagnostic model.

## Search decision pipeline

Search should be observable end to end:

1. Create a normalized request for a show/episode.
2. Fan out only to eligible providers.
3. Normalize candidate releases.
4. Deduplicate equivalent releases.
5. Apply required/rejected word policies.
6. Apply quality-profile acceptance/ranking.
7. Suppress known failed release fingerprints when policy requires it.
8. Score accepted candidates using deterministic components.
9. Persist all decisions and reasons, not only the winner.
10. Submit the winning candidate through a compatible downloader adapter.
11. Persist submission/queue/history state for diagnostics and recovery.

Every decision record should eventually include normalized release name, provider/protocol, parsed episode identity, quality/source/codec traits, size/age/seeders, word-rule matches, quality rank, duplicate/failed state, provider health/rate-limit context, overrides, score, and reason list.

## Operational design

Background work should be represented as observable jobs with IDs, state, timestamps, progress, retries, and errors. Long-running work should not be hidden behind web requests. Provider and downloader failures should use bounded retry/backoff, and repeated failures should surface as health problems rather than silently consuming scheduler cycles.

## UI design goals

The modern interface should make exceptions and next actions obvious. Primary navigation should center on Dashboard, Library, Wanted/Search, Queue/Activity, Calendar, History, Diagnostics, and Settings. Settings should be grouped by user intent rather than legacy code organization. Manual search should show candidate score components and rejection/suppression reasons directly.

## Current architecture checkpoint

Version **12.0.0-dev.2** now includes typed domain models, read-only migration snapshots, provider/downloader adapter contracts, normalized health state, explainable search decisions, failed-release suppression, a repository abstraction, and the first library service. The next increment is persistent compatibility storage plus concrete orchestration and API boundaries.

## Compatibility rule

Until v12 reaches parity, legacy and v12 code may coexist, but v12 logic should be independently testable and should never require the legacy template layer to make core decisions.
