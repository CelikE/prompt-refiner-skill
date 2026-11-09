---
tags: [prompt-refiner]
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep]
---

/prompt-refiner You are a code reviewer. reveiw this function for bugs:

def avg(xs):
    return sum(xs) / len(xs)
