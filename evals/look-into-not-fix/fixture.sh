#!/usr/bin/env bash
set -eu
mkdir -p src test
cat > package.json <<'JSON'
{
  "name": "order-totals",
  "version": "1.0.0",
  "private": true,
  "scripts": { "test": "node --test" }
}
JSON
cat > src/total.js <<'JS'
// Returns the order total in cents.
function total(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

module.exports = { total };
JS
cat > test/total.test.js <<'JS'
const test = require("node:test");
const assert = require("node:assert");
const { total } = require("../src/total");

test("multiplies price by quantity", () => {
  assert.strictEqual(total([{ price: 250, qty: 2 }, { price: 100, qty: 1 }]), 600);
});
JS
