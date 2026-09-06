# TV Manager v12 Architecture Direction

## Runtime shape

TV Manager v12 will evolve toward a layered architecture that separates core decisions from transport and presentation concerns:

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
Owns show/episode inventory, monitoring state, root folders, scans, imports, moves, metadata refresh, and repair operations.

### SearchService
Owns recent/backlog/manual search orchestration, provider capability filtering, candidate normalization, scoring, rejection reasons, deduplication, failed-history checks, and dispatch decisions.

### DownloadService
Owns downloader capabilities, connection tests, queue submission, status mapping, category/label handling, and download reconciliation.

### ProcessingService
Owns completed-download matching, rename/move/copy/hardlink planning, subtitle and metadata sidecars, idempotency, operation journaling, and repair/reprocess actions.

### MigrationService
Owns legacy inspection, mapping, preview, validation, import, cutover, and rollback metadata. It must never silently drop unknown legacy values.

### DiagnosticsService
Owns health/readiness state for database, filesystem, scheduler, metadata/indexers, providers, download clients, background jobs, and migration blockers.

## Search decision model

Every result should be normalised before scoring. A decision record should eventually include:

- normalized release name
- provider and protocol
- parsed show/season/episode identity
- quality/source/codec/release traits
- size, age, seeders/peers when available
- required/rejected/preferred word matches
- quality-profile acceptance and rank
- duplicate/failed-history state
- provider health/rate-limit context
- user overrides
- final score
- accepted/rejected reason list

This gives the UI and logs a single explanation for why automation chose a release.

## Operational design

Background work should be represented as observable jobs with IDs, state, timestamps, progress, retries, and errors. Long-running work should not be hidden behind web requests. Provider and downloader failures should use bounded retry/backoff, and repeated failures should surface as health problems rather than silently consuming scheduler cycles.

## UI design goals

The modern interface should make exceptions and next actions obvious. The primary navigation should center on Dashboard, Library, Wanted/Search, Queue/Activity, Calendar, History, Diagnostics, and Settings. Settings should be grouped by user intent (library, search, downloads, processing, metadata, subtitles, notifications, integrations, system) rather than legacy code organization.

## Compatibility rule

Until v12 reaches parity, legacy and v12 code may coexist, but v12 logic should be independently testable and should never require the legacy template layer to make core decisions.
