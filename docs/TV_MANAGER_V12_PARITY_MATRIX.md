# TV Manager v12 Parity Matrix

This matrix is the acceptance checklist for replacing the legacy runtime. A capability is not complete until behavior, migration, diagnostics, persistence/recovery where applicable, and regression coverage are proven.

| Area | Legacy capability | v12 target | Status |
| --- | --- | --- | --- |
| Library | Existing-show import | Safe scan/import with duplicate detection and preview | Planned |
| Library | Show/season/episode monitoring | Explicit typed monitoring states with bulk operations | Foundation |
| Library | Native persistent storage | Explicit v12 schema separate from legacy DB | dev.3 foundation |
| Library | Anime/sports/air-by-date/scene | Preserve and expose all legacy flags | Migration mapping planned |
| Library | Root directories | Validated root folders, path moves, permissions diagnostics | Planned |
| Metadata | TV indexers and IDs | Adapter model with source provenance and health | Planned |
| Metadata | Artwork/NFO | Regeneration, provenance, repair workflows | Planned |
| Search | Scheduled recent/backlog | Observable restart-safe jobs with explainable decisions | dev.4 scheduler foundation |
| Search | Manual search | Interactive ranked candidate view | Decision engine foundation |
| Search | Provider fan-out | Health-gated aggregation with isolated failures | dev.3 foundation |
| Search | Newznab/Torznab providers | Concrete TV-search/caps adapters with normalized results | dev.4 foundation |
| Search | Required/rejected words | Deterministic scoring and rejection explanation | Foundation |
| Search | Quality profiles | Typed allowed/preferred/cutoff representation | Foundation |
| Search | Failed downloads | Persistent suppression/retry policy | In-memory TTL foundation |
| Search | Persistent decision history | Durable provider/decision/submission records | dev.4 foundation |
| Download | SABnzbd | Health, add URL, category/pause, delete | dev.4 foundation |
| Download | qBittorrent | Health/login, add URL/magnet, category/pause, delete | dev.4 foundation |
| Download | Automatic submission | Normalized submit result and client ID | dev.3 foundation |
| Queue | Queue reconciliation | Recover client state, unknown items, progress, history | dev.3 foundation |
| Queue | Restart persistence | Restore v12 queue/activity state after process restart | dev.4 foundation |
| Jobs | Restart-safe scheduler | Persistent due time, leases, recovery, success/failure accounting | dev.4 foundation |
| Processing | Rename/move/copy/hardlink | Idempotent operation plan and journal | Planned |
| Processing | Multi-episode/specials | Preserve legacy behavior with regression fixtures | Planned |
| Subtitles | Automatic matching/download | Provider adapter + language/forced preferences | Planned |
| Notifications | Existing notifiers | Capability-based notification adapters | Planned |
| Calendar | Upcoming schedule | API-first calendar/feed and responsive UI | Planned |
| History | Search/download/process history | Unified persistent event stream with filters | dev.4 queue/search foundation |
| Diagnostics | Provider/downloader health | Typed health state, latency, diagnostic message | Foundation |
| Diagnostics | Operational dashboard | Unified health dashboard and structured diagnostics | Planned |
| API | Versioned service boundary | Stable JSON API for UI/integrations | dev.4 v1 foundation |
| API | Authentication | Token/session protection appropriate to deployment | dev.4 optional bearer foundation |
| Migration | Existing database/config | Read-only snapshot + validation + rollback | Foundation |
| Deployment | Native/Docker | Reproducible deployment, health/readiness checks | Planned |
| UI | Legacy web interface | Responsive, accessible, configuration-clear interface | Planned |

## Completion rule

A row moves to **Complete** only when its implementation is covered by tests, exposed through stable service boundaries, survives restart/recovery where relevant, is represented in migration validation when applicable, and is documented for operators/users.
