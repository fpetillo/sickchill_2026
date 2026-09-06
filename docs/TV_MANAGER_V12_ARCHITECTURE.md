# TV Manager v12 Architecture Direction

## Runtime shape

TV Manager v12 is evolving toward a layered architecture that separates core decisions from transport and presentation concerns:

- **Domain** — shows, episodes, monitoring, quality, release traits, scoring, policies.
- **Application services** — library, search, queue, post-processing, migration, history, diagnostics, settings.
- **Adapters** — indexers, search providers, download clients, metadata/artwork, subtitles, notifications, filesystem.
- **Persistence** — legacy compatibility during transition plus an explicitly-owned native v12 SQLite schema.
- **Jobs/events** — observable restart-safe background work and durable activity/history.
- **API** — versioned service endpoints; UI never reaches directly into databases or legacy globals.
- **Web UI** — responsive client focused on library state, exceptions, queue/activity, search decisions, diagnostics, and configuration.

## Transition strategy

The current SickChill runtime remains intact while v12 services are introduced beside it. The native v12 repository is intentionally stored separately from the legacy SickChill database. Compatibility wrappers can translate existing functions into stable v12 contracts without forcing a flag-day rewrite.

## Current service/runtime boundaries

### LibraryService
Owns show/episode inventory, monitoring state, wanted calculation, and repository-backed state updates.

### SearchOrchestrator
Owns provider health gating, fan-out, isolated provider errors, candidate aggregation, explainable ranking, failed-release suppression, optional automatic downloader submission, and decision journaling.

### Download adapters
Own downloader health, normalized submission acknowledgement, external client IDs, and delete capability.

### ActivityStore
Owns normalized queue state, progress reconciliation, unknown-client recovery, bounded activity history, and removal events. The dev.3 implementation is in-process; durable persistence is the next step.

### MigrationService
Owns legacy inspection, mapping, preview, validation, import, cutover, and rollback metadata. It must never silently drop unknown legacy values.

### DiagnosticsService target
Will aggregate database, filesystem, scheduler, metadata/indexer, provider, downloader, background-job, migration, and recovery health into one API/UI model.

## Search decision model

Every result is normalized before scoring. A decision model includes or is designed to include normalized release identity, provider/protocol, show/episode identity, quality/source traits, seeders, word-rule matches, quality acceptance/rank, failed history, health context, adjustments, final score, and explicit reason records.

The orchestration layer records a complete run: timestamps, show/episode keys, query, per-provider results/errors/skips, final decision, submission state, client ID, and downloader response text.

## Persistence design

Native v12 persistence must have explicit schema ownership and migrations. Legacy data is an import/compatibility source, not the long-term schema contract. Durable state should eventually include:

- shows, episodes, monitoring and quality assignments
- search decisions and provider execution results
- failed-release suppression history
- queue/download reconciliation state
- processing journals
- scheduler jobs, attempts, retries and errors
- structured history/events
- migration manifests and reconciliation results

## Operational design

Background work will be represented as observable jobs with IDs, state, timestamps, progress, retries, and errors. Provider/downloader failures use bounded failure containment and will gain retry/backoff/circuit-breaking policies. Restart recovery must reconstruct active queue/job state rather than relying on process memory.

## UI design goals

Primary navigation should center on Dashboard, Library, Wanted/Search, Queue/Activity, Calendar, History, Diagnostics, and Settings. Settings are grouped by user intent (library, search, downloads, processing, metadata, subtitles, notifications, integrations, system) rather than legacy code organization.

## Compatibility rule

Until v12 reaches parity, legacy and v12 code may coexist, but v12 logic must remain independently testable and must never require the legacy template layer to make core decisions.
