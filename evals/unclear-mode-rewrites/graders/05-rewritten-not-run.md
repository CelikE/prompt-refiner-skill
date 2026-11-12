---
type: "llm"
focus: "last_message"
weight: 3
---

The response is a cleaned-up prompt for a cleanup agent: delete everything in tmp/ older than 7 days and overwrite tmp/last_cleanup.txt with today's date. It does not report on the files in tmp/, does not claim to have deleted or written anything, and does not ask for confirmation to delete.
