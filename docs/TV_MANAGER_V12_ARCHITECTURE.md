# TV Manager v12 Architecture Direction

## Runtime shape

TV Manager v12 is evolving toward a layered architecture that separates core decisions from transport and presentation concerns:

- **Domain** — shows, episodes, monitoring, quality, release traits, scoring, policies.
- **Application services** — library, search, queue, post-processing, migration, history, diagnostics, settings.
- **Adapters** — indexers, search providers, download clients, metadata/artwork, subtitles, notifications, filesystem.
- **Persistence** — legacy compatibility during transition plus explicitly-owned native v12 SQLite schemas.
- **Jobs/events** — observable restart-safe background work, durable queue/search history, and crash-safe job leases.
- **API** — versioned service endpoints; UI never reaches directly into databases or legacy globals.
- **Web UI** — responsive client focused on library state, exceptions, queue/activity, search decisions, diagnostics, and configuration.

## Transition strategy

The current SickChill runtime remains intact while v12 services are introduced beside it. Native v12 persistence is intentionally stored separately from the legacy SickChill database. Compatibility wrappers translate existing functions into stable v12 contracts without forcing a flag-day rewrite.

## Current service/runtime boundaries

### LibraryService
Owns show/episode inventory, monitoring state, wanted calculation, and repository-backed state updates.

### SearchOrchestrator
Owns provider health gating, fan-out, isolated provider errors, candidate aggregation, explainable ranking, failed-release suppression, optional automatic downloader submission, decision journaling, persistent search recording, and queue creation after successful submission.

### Provider adapters
`NewznabProviderAdapter` and `TorznabProviderAdapter` now provide concrete protocol foundations. They call standard capabilities and TV-search endpoints, normalize RSS/Newznab attributes, and return framework-independent `DownloadCandidate` objects that retain the provider download URL and GUID.

### Download adapters
`SABnzbdAdapter` and `QBittorrentAdapter` provide concrete health, submit, category/pause, and delete foundations behind the stable downloader protocol. Credentials are constructor/config inputs and are not included in runtime search/history payloads.

### PersistentActivityStore / SQLiteRuntimeStore
Own durable queue state, queue progress/state reconciliation, unknown-client recovery, structured event history, and persistent search-decision history. Queue state is reconstructed from SQLite at process startup rather than relying on process memory.

### SQLiteJobStore / SchedulerEngine
Own persistent schedules, due times, job enablement, run/failure accounting, crash-safe leases, and expired-lease recovery. A job must acquire its lease before running; a crashed worker cannot permanently strand the job because the lease expires.

### TVManagerAPI
Owns the versioned `/api/v1` service facade. The current dependency-free WSGI entry point exposes status, library, wanted episodes, queue, history, search history, jobs, due-job execution, and episode-status mutation. Optional bearer-token validation is available at the entry point.

### MigrationService
Owns legacy inspection, mapping, preview, validation, import, cutover, and rollback metadata. It must never silently drop unknown legacy values.

### DiagnosticsService target
Will aggregate database, filesystem, scheduler, metadata/indexer, provider, downloader, background-job, migration, and recovery health into one API/UI model.

## Search decision model

Every result is normalized before scoring. A decision model includes or is designed to include normalized release identity, provider/protocol, show/episode identity, quality/source traits, seeders, word-rule matches, quality acceptance/rank, failed history, health context, adjustments, final score, and explicit reason records.

The orchestration layer records a complete run: timestamps, show/episode keys, query, per-provider results/errors/skips, final decision, submission state, client ID, and downloader response text. In dev.4 that record can be persisted in the v12 runtime database for API/UI inspection after restart.

## Persistence design

Native v12 persistence has explicit schema ownership. Legacy data is an import/compatibility source, not the long-term schema contract. Current durable state includes show/episode inventory in the native repository plus queue state, structured event history, search decisions, and scheduler metadata in the runtime store.

Still to be persisted or expanded:

- failed-release suppression history
- provider/downloader health samples and circuit-breaker state
- completed-download processing journals
- richer scheduler attempts, progress, cancellation and worker identity
- migration manifests and reconciliation results
- configuration metadata with secret references rather than plaintext secret history

## Operational design

Background work is moving to observable, restart-safe jobs. Job leases prevent duplicate execution and recover after crashes. Provider/downloader failures are contained at adapter boundaries and will gain bounded retry/backoff and circuit-breaking policies. Queue/job recovery must reconstruct state from durable storage and reconcile it with external clients instead of assuming process memory is authoritative.

## API design rules

- `/api/v1` is the first stable transport boundary; future web clients should depend on API/service contracts rather than legacy templates or globals.
- API serialization is explicit and JSON-safe for dataclasses, enums, dates and datetimes.
- State-changing operations go through application services/repositories.
- Authentication is optional for local development but should be mandatory for exposed deployments.
- Manual search, provider/client testing, settings, diagnostics, backup/restore and processing endpoints are the next expansion areas.

## UI design goals

Primary navigation should center on Dashboard, Library, Wanted/Search, Queue/Activity, Calendar, History, Diagnostics, and Settings. Settings are grouped by user intent (library, search, downloads, processing, metadata, subtitles, notifications, integrations, system) rather than legacy code organization.

## Compatibility rule

Until v12 reaches parity, legacy and v12 code may coexist, but v12 logic must remain independently testable and must never require the legacy template layer to make core decisions.
