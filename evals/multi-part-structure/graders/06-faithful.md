---
type: "llm"
focus: "last_message"
weight: 3
---

The rewritten prompt keeps all of: cursor-based pagination for GET /invoices with a default page size of 50; a CSV export that streams rows instead of loading everything into memory; tests for both; updating docs/api.md; not changing the auth middleware; reporting anything odd in the invoice model without fixing it. It adds no requirement that was not in the request.
