# IamCarla MCP connector — changelog

The version here is `MCP_SERVER_VERSION` in `new_visu/mcp_connector/__init__.py`; it is what
`initialize` reports, what `/mcp/manifest.json` shows, and what `server.json` publishes.

## 1.1.0 — 2026-09-30

- Staff connections: a Collaboratore, a Segretaria or the Super Admin can connect their own agent
  and get the read-only agency tool set (`staff` scope, never client write levels). The Super Admin's
  agent sees every client through the collaboratore tools; a Collaboratore's is scoped to his book; a
  Segretaria's to her assignments.
- Pairing codes for staff: the Super Admin issues them for any staff member and for himself (from
  his own profile); a Collaboratore issues them for the segretarie on his book.
- "Collega un agente" panel on the profile page: endpoint, steps, copy buttons and install links for
  Claude, Claude Code, Cursor and VS Code, plus `GET /api/account/mcp-connect`.
- Ghost (impersonation) sessions cannot consent, list, revoke or issue anything on the
  impersonated account.

## 1.0.0 — 2026-09-30

Initial public release.

- Streamable-HTTP endpoint `POST /mcp` (JSON-RPC 2.0; protocol versions 2025-06-18, 2025-03-26,
  2024-11-05). `GET /mcp` answers 405; an event-stream-only `Accept` gets the reply as one SSE event.
- 117 tools over customers, leads, calendar, WhatsApp, tasks, automations, profile, site, social,
  reporting and help, each with a risk level and a confirmation tier (`none`, `auto_undo`,
  `confirm`, `confirm_typed`). Public catalog at `/mcp/manifest.json`.
- Owner-confirmed writes: sensitive actions return a `pending_id` and run only after the owner
  approves them in IamCarla. Destructive actions need a typed confirmation and can never be approved
  from a connector. Small changes return an `undo_token` (120 s window).
- OAuth 2.1: RFC 8414 / RFC 9728 discovery, dynamic client registration (RFC 7591, public clients),
  PKCE S256 only, `resource` audience binding (RFC 8707), access token 1 h, refresh token 30 d with
  rotation and reuse detection.
- Pairing code: connecting an agent requires a single-use code that the owner's collaboratore
  generates in IamCarla; the consent screen refuses without it and shows the redirect host.
- Staff controls per client: connector on/off and a permission ceiling, applied to every call.
- Idempotency keys on write tools (24 h replay window), per-token rate limit, cap on queued
  confirmations per hour, results containing customer or web text flagged `untrusted`.
