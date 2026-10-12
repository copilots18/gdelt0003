const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const jsonPath = path.join(__dirname, '..', 'data', 'highlights.json');
const fileText = fs.readFileSync(jsonPath, 'utf8');
const highlights = JSON.parse(fileText);

test('default highlight data is populated', () => {
  assert.ok(Array.isArray(highlights));
  assert.ok(highlights.length >= 3);
  const ready = highlights.filter((item) => item.status === 'ready');
  assert.ok(ready.length >= 3);
});

test('white-house example exists in the default batch', () => {
  const hasWhiteHouse = highlights.some((item) => item.source_channel?.includes('White House'));
  assert.equal(hasWhiteHouse, true);
});

test('batch items contain readable timing metadata', () => {
  const first = highlights[0];
  assert.ok(first.start_sec >= 0);
  assert.ok(first.end_sec > first.start_sec);
  assert.ok(first.score >= 80);
});
