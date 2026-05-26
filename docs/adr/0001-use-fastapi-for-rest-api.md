# 0001. Use FastAPI for the REST API

## Status

Accepted

## Context

iCloud Access Broker exposes a broker-owned REST API to downstream agents and scripts. The API must stay at the
input-adapter boundary so the domain and application layers remain independent of web framework concerns.

## Decision

Use FastAPI for the REST input adapter.

FastAPI and Pydantic request/response models must stay inside `src/icloud_access_broker/adapters/input/http/`.
Routes call application use cases through application DTOs and ports rather than importing infrastructure details into
the application or domain layers.

## Consequences

- The project depends on FastAPI and an ASGI server for local serving.
- OpenAPI documentation is available from the generated FastAPI app.
- HTTP tests can use FastAPI's `TestClient`.
- Application and domain modules must not import FastAPI, Starlette, or Pydantic HTTP models.