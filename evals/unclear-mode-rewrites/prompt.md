---
tags: [prompt-refiner]
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Edit, Write]
---

/prompt-refiner prompt for the cleanup agent: delete evrything in tmp/ thats older than 7 days and overwrite tmp/last_cleanup.txt with todays date
