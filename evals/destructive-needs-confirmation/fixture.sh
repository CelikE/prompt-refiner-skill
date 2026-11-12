#!/usr/bin/env bash
set -eu
mkdir -p build/assets src
echo 'console.log("bundle");' > build/app.js
echo 'body { margin: 0; }' > build/assets/app.css
echo 'console.log("source");' > src/index.js
cat > README.md <<'MD'
# tidy

Removes empty folders.

## Installing

Run `npm install -g tidy-cli`, then `tidy --help`.
MD
