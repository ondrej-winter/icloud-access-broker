# iCloud Access Broker

`icloud-access-broker` is a single-user, policy-enforcing broker for personal iCloud access.

Apple app-specific passwords provide broad protocol access instead of OAuth-style scoped delegation. This
broker is intended to hold those credentials internally and expose a narrower REST API protected by broker-issued
tokens with explicit capabilities such as `calendar:read`, `calendar:write`, `mail:read`, and `mail:send`.

The broker-enforced scopes are an application-layer security boundary, not Apple-enforced delegation. Treat this
service as a sensitive credential broker: clients must not receive the Apple app-specific password, and the broker
must not expose unrestricted raw CalDAV, CardDAV, IMAP, or SMTP passthrough that would bypass policy checks.

The repository is bootstrapped with a hexagonal architecture so domain and application code stay independent of infrastructure and external interfaces.

## Project identifiers

| Surface | Value |
| --- | --- |
| GitHub repository | `icloud-access-broker` |
| PyPI package | `icloud-access-broker` |
| Python import | `icloud_access_broker` |
| CLI command | `icloud-access-broker` |
| Service name | iCloud Access Broker |

## Requirements

- Python 3.14 or newer
- [`uv`](https://docs.astral.sh/uv/) for dependency and environment management

## Product scope

Initial scope is a self-hosted broker for one operator's iCloud account and trusted downstream agents or scripts.

| Area | Apple protocol | Broker responsibility |
| --- | --- | --- |
| Calendar | CalDAV | Expose scoped REST operations for calendar reads/writes without raw CalDAV passthrough. |
| Mail | IMAP/SMTP | Expose scoped REST operations for mail reads and sending without raw IMAP/SMTP passthrough. |
| Contacts | CardDAV | Potential later scope for scoped contact reads/writes. |

The MVP does not require data minimization or redaction. The primary permission boundary is capability scoping:
a token with `calendar:read` can read allowed calendar resources but cannot write events, and a token with
`mail:read` cannot send mail.

## Setup

Install the development environment:

```bash
uv sync --group dev
```

Run the CLI:

```bash
uv run icloud-access-broker
uv run icloud-access-broker --version
```

Run the REST API locally:

```bash
export ICLOUD_ACCESS_BROKER_ADMIN_SECRET='<admin-secret>'
uv run icloud-access-broker-api
```

The HTTP adapter also reads a local `.env` file when present:

```dotenv
ICLOUD_ACCESS_BROKER_ADMIN_SECRET=<admin-secret>
```

The development server listens on `http://127.0.0.1:8000` and currently exposes:

- `GET /health`
- `GET /version`
- `POST /admin/tokens`
- `DELETE /admin/tokens/{token_id}`
- `GET /capabilities/calendar/read`

Token lifecycle endpoints are protected by an HTTP `X-Admin-Secret` header. Configure
`ICLOUD_ACCESS_BROKER_ADMIN_SECRET` before starting the server; never expose the API outside a trusted local
environment with a weak or shared secret.

Issue a scoped broker token:

```bash
curl -X POST http://127.0.0.1:8000/admin/tokens \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Secret: <admin-secret>' \
  -d '{"label":"calendar agent","capabilities":["calendar:read"]}'
```

Use the returned one-time `token` value as a bearer token:

```bash
curl http://127.0.0.1:8000/capabilities/calendar/read \
  -H 'Authorization: Bearer <broker-token>'
```

Revoke a token by id:

```bash
curl -X DELETE http://127.0.0.1:8000/admin/tokens/<token-id> \
  -H 'X-Admin-Secret: <admin-secret>'
```

Issued token secrets are returned only when created. The MVP stores token metadata in memory, so tokens are lost when
the process restarts. Durable token persistence, audit logs, and rate limiting are deferred.

## Quality checks

Run the local quality gate before handing off changes:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

## Architecture

The codebase uses a `src/` layout with hexagonal boundaries:

| Layer | Directory | Responsibility |
| --- | --- | --- |
| Domain | `src/icloud_access_broker/domain/` | Pure business concepts and invariants. No I/O or framework imports. |
| Application | `src/icloud_access_broker/application/` | Use cases, ports, and application boundary DTOs. Depends inward on the domain only. |
| Input adapters | `src/icloud_access_broker/adapters/input/` | Driving interfaces such as the CLI. Map external input to application ports. |
| Output adapters | `src/icloud_access_broker/adapters/output/` | Driven infrastructure integrations such as external APIs or persistence. |

Tests mirror these responsibilities under `tests/unit/` and `tests/integration/`.

See `docs/product-intent.md` for the confirmed product intent that guides this repository.
See `docs/adr/0001-use-fastapi-for-rest-api.md` for the REST framework decision.