# TV Manager v12 Parity Matrix

This matrix is the acceptance checklist for replacing the legacy runtime. A capability is not considered complete until behavior, migration, diagnostics, and regression coverage are all proven.

| Area | Legacy capability | v12 target | Status |
| --- | --- | --- | --- |
| Library | Existing-show import | Safe scan/import with duplicate detection and preview | Planned |
| Library | Show/season/episode monitoring | Explicit typed monitoring states with bulk operations | Foundation |
| Library | Anime/sports/air-by-date/scene | Preserve and expose all legacy flags | Migration mapping planned |
| Library | Root directories | Validated root folders, path moves, permissions diagnostics | Planned |
| Metadata | TV indexers and IDs | Adapter model with source provenance and health | Planned |
| Metadata | Artwork/NFO | Regeneration, provenance, repair workflows | Planned |
| Search | Scheduled recent/backlog | Observable jobs with explainable decisions | Planned |
| Search | Manual search | Interactive ranked candidate view | Planned |
| Search | Newznab/Torznab/native providers | Typed adapters with capability and health checks | Planned |
| Search | Required/rejected words | Deterministic scoring and rejection explanation | Foundation |
| Search | Quality profiles | Typed allowed/preferred/cutoff representation | Foundation |
| Search | Failed downloads | Persistent suppression/retry policy | Planned |
| Download | NZB/torrent clients | Typed adapters, queue state, test connection | Planned |
| Processing | Rename/move/copy/hardlink | Idempotent operation plan and journal | Planned |
| Processing | Multi-episode/specials | Preserve legacy behavior with regression fixtures | Planned |
| Subtitles | Automatic matching/download | Provider adapter + language/forced preferences | Planned |
| Notifications | Existing notifiers | Capability-based notification adapters | Planned |
| Calendar | Upcoming schedule | API-first calendar/feed and responsive UI | Planned |
| History | Search/download/process history | Unified event stream with filters | Planned |
| Diagnostics | Logs and provider tests | Health dashboard and structured diagnostics | Planned |
| Migration | Existing database/config | Read-only snapshot + validation + rollback | Foundation |
| Deployment | Native/Docker | Reproducible deployment, health/readiness checks | Planned |
| UI | Legacy web interface | Responsive, accessible, configuration-clear interface | Planned |

## Completion rule

A row moves to **Complete** only when its implementation is covered by tests, exposed through stable service boundaries, represented in migration validation when applicable, and documented for operators/users.
