# TV Manager v12 — Development Release Notes

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

### Next

Subsequent v12 increments will map the complete legacy schema/configuration, add a compatibility service layer, introduce typed provider/downloader adapters, expose a stable service API, and build the modern responsive interface against those APIs.
