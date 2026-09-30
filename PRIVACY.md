# Privacy

This note covers the MCP connector specifically. The general IamCarla policies apply in full:

- Privacy policy: https://iamcarla.it/privacy
- Terms of service: https://iamcarla.it/termini
- AI policy: https://iamcarla.it/ai-policy

## Whose data

A connection acts **only on the account of the owner who authorized it**, within the permission level they chose. The connector never aggregates data across accounts and never exposes one professional's data to another.

## What an agent can access

Depending on the granted level (see [README.md](README.md#permission-levels)):

- **Read**: the owner's customers and leads (names, phone numbers, e-mail addresses, notes, tags, history), calendar events, WhatsApp and social conversations, tasks, automations, site content, social posts, reports, and IamCarla help content.
- **Write (undoable)**: lead status flags, task completion, automation on/off, small lead edits.
- **Write (owner-confirmed)**: proposals to send messages, create or move appointments, add customers or leads, record sales, edit profile/site/social content. None of these run until the owner approves them in IamCarla.

Personal data of the owner's customers therefore flows to the owner's chosen AI client. The owner remains the data controller for their customers' data; the AI client's provider is the owner's choice and their processor. IamCarla does not send account data to any AI provider on its own as part of this connector.

## What we store about the connection

- The connection itself: agent name, permission scopes, creation, expiry, last-use and revocation timestamps, and (for OAuth grants) the registered client id and which staff member issued the pairing code.
- Hashes of access, refresh and pairing codes (never the plaintext).
- An audit trail of every tool call: tool name, truncated arguments and result (500 characters), timestamp, agent name.
- Idempotency records for write calls, kept 24 hours.

Authorization codes expire after 10 minutes and pairing codes after 15 minutes; both are single use. Revoked and expired connections remain in the audit history for accountability.

## Deletion

Revoking a connection stops all access immediately. Deleting an IamCarla account deletes its connections, codes and idempotency records; audit entries follow the account's audit-retention rules described in the privacy policy.

## Contact

info@iamcarla.it
