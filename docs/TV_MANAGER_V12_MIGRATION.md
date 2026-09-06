# TV Manager v12 Migration Workflow

The v12 migration path is designed to protect existing SickChill installations and make every transformation auditable.

## Snapshot first

Run the exporter against a stopped or otherwise quiescent SickChill instance when possible:

```bash
python tools/tvmanager_v12_migrate.py /path/to/sickbeard.db \
  --config /path/to/config.ini \
  --output tv-manager-v12-migration.json
```

The database is opened using SQLite read-only mode. The exporter does not alter the source database.

## What the snapshot contains

- SQLite `user_version`
- Migration-relevant legacy tables when present
- Column names and all row values for exported tables
- Optional legacy INI configuration sections/keys
- Counts for every exported table
- Warnings for expected tables that are missing
- Warnings for existing tables that do not yet have an explicit v12 migration handler

## Cutover rules

1. Keep the original SickChill database and configuration untouched until validation passes.
2. Treat the JSON manifest as an intermediate migration artifact, not as the live v12 database.
3. Preserve legacy identifiers during import so reconciliation and rollback remain possible.
4. Never silently discard an unknown status, provider, quality value, indexer identifier, or configuration key. Record it as a migration warning and require an explicit mapping.
5. Compare pre/post migration counts for shows, episodes, history, scene data, and configured integrations.
6. Verify library paths and file existence without moving media during preview mode.
7. Run provider/download-client connection tests before enabling scheduled searches.
8. Enable v12 automation only after a migration validation report has no blocking errors.

## Required parity validation

Before v12 becomes the default runtime, migration validation should confirm:

- Show count and indexer IDs
- Season/episode count per show
- Episode status and downloaded quality
- Episode file locations
- Pause/anime/sports/air-by-date/scene flags
- Root directories
- Quality profiles and custom/release rules
- Provider enablement and credentials references
- Download client configuration
- Naming/post-processing configuration
- Subtitle languages and provider preferences
- Notification integrations
- Search/download history and failed-download memory where compatible
- Scene/XEM exceptions and numbering

## Rollback

Rollback must remain possible until the user explicitly completes migration. The original SickChill database/configuration and media files should remain valid. Any v12 file moves or renames performed after cutover need an operation journal so they can be reversed independently from database rollback.
