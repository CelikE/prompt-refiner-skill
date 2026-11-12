---
tags: [prompt-refiner]
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep]
---

/prompt-refiner Improve this prompt: need u to do a few things in the billing service. first add pagination to GET /invoices, cursor based, default page size 50. then make the csv export stream rows instead of loading everthing into memory. write tests for both. update docs/api.md when done. dont change the auth middleware. and if u see anything weird in the invoice model tell me but dont fix it
