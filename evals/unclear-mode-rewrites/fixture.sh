#!/usr/bin/env bash
set -eu
mkdir -p tmp
echo 'old report' > tmp/report-old.csv
echo 'new report' > tmp/report-new.csv
echo '2026-01-01' > tmp/last_cleanup.txt
