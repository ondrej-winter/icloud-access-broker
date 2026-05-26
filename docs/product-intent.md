# iCloud Access Broker product intent

## Confirmed intent

Build a general personal iCloud access broker that holds Apple app-specific credentials internally and exposes
broker-issued scoped REST API tokens to downstream clients.

## User

The first user is the repository owner using personal AI agents or scripts against their own iCloud Mail, Calendar,
and potentially Contacts data.

## Why this exists

Apple provides app-specific passwords for personal iCloud accounts, but not proper OAuth-style scoped delegation for
Mail, Calendar, or Contacts. The broker creates the missing permission boundary at the application layer.

## Success criteria

An operator can issue a token to an agent with explicit capabilities such as `calendar:read`, `calendar:write`,
`mail:read`, `mail:send`, or narrower future scopes. The broker enforces those capabilities even though it holds a
broad Apple app-specific password internally.

## Constraints

- Scope enforcement is broker-enforced, not Apple-enforced.
- The broker is a sensitive credential holder and must never expose Apple app-specific passwords to clients.
- Clients must not control raw CalDAV, CardDAV, IMAP, or SMTP protocol requests in ways that bypass broker policy.
- The first product target is single-user/self-hosted, not multi-user SaaS.

## Out of scope for the initial product direction

- Multi-user SaaS account management.
- Apple OAuth or Apple-enforced scoped delegation.
- Data minimization or redaction as a required MVP feature.
- Unrestricted raw protocol proxying.