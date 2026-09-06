# TV Manager v12 Status

Current development version: **12.0.0-dev.4**

This branch remains additive to the legacy SickChill runtime while v12 capabilities are implemented and validated.

## Implemented

### 12.0.0-dev.1 foundation
- Typed domain models for shows, episodes, episode states, quality profiles, and candidates.
- Deterministic candidate scoring and read-only legacy migration snapshot tooling.
- Initial migration, parity, architecture, and regression-test foundation.

### 12.0.0-dev.2 reliability and service layer
- Typed provider/downloader contracts and normalized health diagnostics.
- Explainable candidate decisions and time-bounded failed-release suppression.
- Repository abstraction, in-memory reference storage, and library service.

### 12.0.0-dev.3 persistent runtime and orchestration
- Native SQLite v12 show repository with explicit schema ownership and typed round-trip serialization.
- Legacy/provider callable wrappers behind stable v12 adapter contracts.
- Search orchestrator with provider health gating, fan-out, candidate aggregation, deterministic selection, optional automatic submission, and decision journaling.
- Queue/activity model with progress/state reconciliation, unknown-client recovery, bounded history, and manual removal tracking.
- Regression tests for persistence, automatic search/submission, and queue recovery.

### 12.0.0-dev.4 restart-safe platform services
- Restart-safe SQLite runtime store for queue state, event history, search decision history, and scheduler metadata.
- Persistent activity facade that restores queue state after process restarts and journals queue changes transactionally.
- Persistent scheduler with due-time calculation, enabled/disabled jobs, crash-safe leases, failure accounting, and expired-lease recovery.
- Concrete Newznab and Torznab adapters using standard TV search/capabilities endpoints and normalized RSS/Newznab attributes.
- Download candidates now preserve provider download URL and GUID so accepted releases can be handed to concrete clients.
- Concrete SABnzbd and qBittorrent adapter foundations with health checks, submission, categories, pause behavior, and delete support.
- Search orchestration can persist complete decision history and automatically create activity/queue entries after successful submission.
- Dependency-free versioned `/api/v1` JSON facade for status, library, wanted episodes, queue, history, search history, jobs, due-job execution, and episode status updates.
- Optional bearer-token protection for the WSGI API entry point.
- Regression tests for restart persistence, scheduler recovery/failure accounting, Newznab parsing, persisted search/queue flow, and v1 API behavior.

## Next code milestones

- Complete SickChill legacy schema/config mapping into native v12 storage with reconciliation and parity reports.
- Persist failed-release suppression and richer downloader queue reconciliation across restarts.
- Add retry/backoff, rate-limit/circuit-breaker behavior, capability discovery, and secure secret/config storage around concrete adapters.
- Add downloader queue polling for SABnzbd/qBittorrent and map completed/failed states into processing jobs.
- Expand the v1 API with manual/interactive search, provider tests, downloader tests, settings, diagnostics, backup/restore, and OpenAPI documentation.
- Add a restart-safe background runner with concurrency limits, cancellation, progress, and graceful shutdown.
- Begin the modern responsive web interface exclusively against the v12 API.
- Add cutover, rollback, backup, and full migration/parity regression tooling.

The legacy application remains the operational baseline until parity and migration validation demonstrate that v12 can replace it safely.
