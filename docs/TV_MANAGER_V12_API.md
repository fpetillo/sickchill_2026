# TV Manager v12 API — dev.4

TV Manager v12 introduces a versioned JSON service boundary at `/api/v1`. The API is intentionally implemented above the domain/service/repository layers so the future web interface, automation clients, and diagnostics tools do not depend on legacy templates, globals, or database details.

## Current endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/status` | Runtime/version summary and high-level counts |
| GET | `/api/v1/library` | Show/episode inventory; `include_paused=false` filters paused shows |
| GET | `/api/v1/wanted` | Wanted/unknown/failed episodes from active shows |
| GET | `/api/v1/queue` | Restart-safe queue snapshot |
| GET | `/api/v1/history?limit=100` | Persistent queue/activity event history |
| GET | `/api/v1/search/history?limit=50` | Persistent search decisions and provider outcomes |
| GET | `/api/v1/jobs` | Persistent scheduler job state |
| POST | `/api/v1/jobs/run-due` | Execute currently due jobs through the configured scheduler |
| POST | `/api/v1/episode/status` | Update one episode through `LibraryService` |

## Episode status update

Example request body:

```json
{
  "indexer": "tvdb",
  "indexer_id": "42",
  "season": 1,
  "number": 1,
  "status": "skipped"
}
```

The API delegates the mutation to `LibraryService`; it does not write directly to the database.

## Authentication

`create_wsgi_app()` accepts a `TVManagerAPI` instance. If `api_token` is set, requests must include:

```text
Authorization: Bearer <token>
```

The current token mechanism is intentionally small and suitable as a development/reverse-proxy boundary. Production exposure should use TLS and may add session/OIDC/API-key management without changing the application-service contracts.

## WSGI entry point

```python
from tvmanager_v12 import TVManagerAPI, create_wsgi_app

api = TVManagerAPI(library, runtime_store, job_store, scheduler, api_token="...")
application = create_wsgi_app(api)
```

The WSGI layer has no new third-party dependency. It can be hosted behind an existing WSGI server or adapted later to ASGI/FastAPI/another transport while retaining the same domain and application services.

## API design rules

- Keep transport serialization separate from domain logic.
- Route state mutations through application services/repositories.
- Never return adapter credentials, API keys, passwords, cookies, or authorization headers.
- Keep `/api/v1` backward compatible once promoted beyond development status.
- Add pagination/filtering before unbounded collections can become large.
- Return explainable search decisions so a user can see why a release was accepted, rejected, or suppressed.
- Expose provider/downloader health and background-job state instead of requiring raw-log inspection.

## Next API expansion

The next increments should add manual/interactive search, provider and downloader connection tests, queue actions, failed-release controls, diagnostics, settings with secret references, backup/restore, migration preview/reconciliation, post-processing actions, calendar endpoints, and a machine-readable OpenAPI contract.
