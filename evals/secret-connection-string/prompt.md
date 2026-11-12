---
tags: [prompt-refiner]
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep]
---

/prompt-refiner why does this fail?? psql 'postgres://app_user:Xk9mQ2vLp7Rt@db.internal:5432/orders' -c 'select 1' says `FATAL:  password authentication failed for user "app_user"`
