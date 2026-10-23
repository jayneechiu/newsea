import assert from "node:assert/strict";
import { test } from "node:test";
import { loginPath, safeNextPath } from "./redirect.ts";

test("same-site paths are kept as the post-login destination", () => {
  assert.equal(safeNextPath("/signals/abc?x=1"), "/signals/abc?x=1");
});

test("missing or off-site destinations fall back to home", () => {
  for (const next of [null, "", "https://evil.example", "//evil.example", "/\\evil.example", "javascript:alert(1)"]) {
    assert.equal(safeNextPath(next), "/");
  }
});

test("login links carry the destination and optional sign-up mode", () => {
  assert.equal(loginPath("/newsletter"), "/login?next=%2Fnewsletter");
  assert.equal(loginPath("/", "signup"), "/login?next=%2F&mode=signup");
});
