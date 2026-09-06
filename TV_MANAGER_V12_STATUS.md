# TV Manager v12 Status

Current development version: **12.0.0-dev.3**

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

## Next code milestones

- Complete SickChill legacy schema/config mapping into native v12 storage with reconciliation reports.
- Persist search decisions, queue state, failed-release history, jobs, and events across restarts.
- Concrete Newznab/Torznab and torrent/NZB downloader adapters with retry/backoff and capability discovery.
- Versioned service API for library, episodes, search, queue, history, configuration, jobs, and diagnostics.
- Background scheduler/job engine with restart recovery, concurrency limits, and observable progress.
- Modern responsive web interface developed exclusively against the v12 service API.
- Cutover, rollback, backup, and full parity regression tooling.

The legacy application remains the operational baseline until parity and migration validation demonstrate that v12 can replace it safely.
