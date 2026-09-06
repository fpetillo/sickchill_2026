# TV Manager v12 Status

Current development version: **12.0.0-dev.1**

This branch establishes the additive v12 modernization foundation without changing the legacy SickChill runtime path.

## Implemented in this baseline

- Typed framework-independent domain objects for shows, episodes, episode states, quality profiles, and download candidates.
- Deterministic candidate scoring with quality acceptance, preferred quality ranking, required words, rejected words, seeders, and score adjustments.
- Read-only legacy SQLite migration exporter.
- Optional legacy INI configuration capture.
- Migration manifest counts, warnings, unknown-table reporting, and SQLite schema version capture.
- CLI migration snapshot tool.
- Regression tests for scoring, episode tracking, and legacy-row preservation.
- v12 architecture/capability roadmap and migration workflow documentation.

## Next code milestones

- Full legacy schema/config mapping and migration validation report.
- Compatibility repository/service layer around current SickChill data.
- Typed provider and downloader adapter contracts with health checks.
- Search-decision explanation model and failed-download suppression service.
- Versioned service API for library, episodes, search, queue, history, configuration, and diagnostics.
- Modern web interface developed against the service API.
- Cutover, rollback, backup, and parity regression tooling.

The legacy application remains the operational baseline until parity checks demonstrate that v12 can replace it safely.
