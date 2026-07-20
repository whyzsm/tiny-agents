---
name: harmonyos-app-store-self-check
description: "Audit HarmonyOS applications for AppGallery/AGC release readiness. Use when users ask for 鸿蒙上架自检、应用市场审核、AGC发布前检查、签名/隐私/权限/截图核对或 release 包门禁，especially for Stage-model projects with module.json5, build-profile.json5, hvigorw, and local-first data constraints."
---

# HarmonyOS App Store Self Check

## Overview

Audit a HarmonyOS/OpenHarmony project before an AppGallery/AGC submission. The
output is an evidence-backed release gate, not a promise that Huawei will
approve the application. Keep three kinds of evidence separate:

- `confirmed`: observed in the repository, a successful command, a device run,
  or an AGC result supplied by the user;
- `baseline`: a useful check derived from the visible
  `harmonyos-code-workshop` material;
- `unverified`: a current AGC policy, account setting, device behavior, or
  artifact property that was not checked.

This Skill is for release readiness and submission preparation. It does not
upload packages, create certificates, modify signing material, or silently fix
project files.

## Triggers And Inputs

Use it for requests such as:

- “帮我做鸿蒙应用上架自检，找出 AGC 审核阻断项。”
- “检查这个 HarmonyOS Stage 项目的 release 包、隐私、权限、签名和应用市场截图。”
- “我的鸿蒙 AppGallery 发布前还缺什么证据？”

Accept a project root, an optional target module/product, target API/OS version,
AGC listing metadata, privacy/legal material, screenshots, and an already-built
HAP/APP. If a path or artifact is not supplied, inspect the repository first;
ask only for information that blocks the next useful check.

## Outputs And Completion

Return a Chinese report unless the user asks for another language. Include:

1. `READY`, `BLOCKED`, or `UNVERIFIED` overall gate status.
2. A flat table with check ID, status (`PASS`/`FAIL`/`BLOCKED`/`UNVERIFIED`),
   severity (`P0`/`P1`/`P2`), evidence path or command, and remediation.
3. A short release artifact checklist and the exact commands that were run.
4. Assumptions, unavailable AGC/device evidence, and the next smallest action.

The gate is `READY` only when no P0/P1 release blocker remains and all checks
that are required for the chosen product are confirmed. Otherwise use
`BLOCKED`; use `UNVERIFIED` when the project may be ready but evidence is
missing. Never turn an unrun check into a pass.

## Workflow

1. **Route the request.** This Skill handles release-readiness audits directly.
   For policy/API/version questions that require authoritative Huawei sources,
   search the official documentation or AGC console and cite the source. For
   project code fixes, fix only after presenting the audit findings and getting
   user approval. For broad functional/UI/interaction review, treat it as a
   separate quality-review request. Do not expand the audit scope into unrelated
   changes.
2. **Inspect project shape.** Read repository instructions first. Locate
   `AppScope/app.json5`, each `module.json5`, `build-profile.json5`,
   `entry/build-profile.json5`, `hvigorfile.ts`, `oh-package.json5`,
   `main_pages.json`, source modules, tests, privacy/legal pages, listing
   screenshots, and project QA/release notes. Record the target product,
   module, API level, and build mode.
3. **Run the static preflight.** From this package, run:

   ```bash
   python3 scripts/check_harmony_release.py --project-root <project-root> --format text
   ```

   Add `--forbid-network` for a local-first app and `--strict` when the report
   should exit non-zero on failures. The helper is advisory; inspect every
   finding before making a release decision.
4. **Check identity and packaging.** Verify bundle name, label, version code,
   version name, module/ability entry, route registry, device types, target and
   compatible SDKs, and release-mode configuration. Confirm that the artifact
   being reviewed is the same product/version represented in the listing.
5. **Check privacy, permissions, and data handling.** Map every declared or
   runtime-sensitive permission to a real feature and user-visible disclosure.
   Check minimum permission scope, denial/error behavior, privacy policy,
   deletion/retention language, third-party SDK disclosure, and any children,
   advertising, payment, health, location, or account flows that are actually
   present. For photos, verify that binaries remain app-local and only local
   references reach SQLite. Treat unexplained network access or remote-sync
   claims as a blocker for local-first projects.
6. **Check release security.** Require a release build, a valid AGC signing
   chain and profile for the target bundle, and a reproducible artifact path.
   Scan tracked and staged files for certificates, profiles, keystores,
   passwords, tokens, home-directory paths, and debug-only configuration. Do
   not print secret values; report only the path and kind of leak.
7. **Check product and listing evidence.** Confirm that the name, icon,
   description, screenshots, claims, privacy URL, and supported devices match
   implemented behavior. Screenshots must show real, reachable product states;
   remove placeholders, fake social data, and claims of synchronization or
   capabilities not implemented. Check Chinese user-facing loading, empty,
   error, permission-denied, and deletion feedback where the project requires
   it.
8. **Run verification in increasing cost.** Run repository validation scripts
   and `git diff --check`; run the project release/HAP build with its own
   `hvigorw`; then run the manual QA script on emulator/device for cold start,
   offline behavior, core CRUD, permission denial, restart persistence, data
   deletion, migration, and crash/error recovery. Label static-only checks and
   unavailable device/AGC checks explicitly.
9. **Synthesize the gate.** Deduplicate findings, classify P0 (submission or
   core workflow blocked, data/privacy/security can be false or lost), P1
   (must fix before release), and P2 (lower-risk polish or evidence gap), then
   report the smallest remediation order. Ask before edits, signing, upload,
   commit, push, or other external side effects.

## Harmony Wardrobe Adapter

When the inspected repository is Harmony Wardrobe / `衣不缺`, enforce its
project facts in addition to the generic checks:

- `io.wardrobe.tiny` is the bundle name and the product is a Stage app for
  phone/tablet. Read the resource label instead of assuming a display string.
- The app is local-first: SQLite business tables are the source of truth,
  photos are copied to app-local storage, and SQLite stores only local
  URI/path references. No `INTERNET` permission, backend, remote sync, fake
  social feed, or “待同步” claim may be introduced without an explicit scope
  change.
- Read `docs/legal/privacy-policy.html`, `docs/legal/user-agreement.html`,
  `docs/architecture.md`, `docs/qa/manual-test-script.md`, and
  `docs/delivery/first-release-verification.md` when present. Use
  `docs/appgallery/screenshots/` as listing evidence only after checking that
  the screens are reachable and current.
- A delete flow is not complete until the business row, derived search index,
  and orphaned local media are handled consistently. Permission denial and
  local media-copy failure must remain visible to the user.
- Treat a `build-profile.json5` containing `signingConfigs`, passwords,
  `.p12`/`.cer`/`.p7b`, or `/Users/` paths as local signing material, not as a
  publishable repository artifact. Preserve the user's uncommitted changes and
  redact values in reports.
- If UI changes are proposed, read `docs/background/yibuque-design.md` first;
  do not turn this release audit into an unrelated redesign.

## Evidence Rules

The visible workshop source provides a release-flow baseline: developer/AGC
registration, certificate/profile preparation, signed HAP/APP packaging, listing
metadata, privacy/permission checks, and submission. Its “上架合规必查” bullets
are guidance, not the current official policy. For policy-sensitive questions,
consult current official Huawei documentation or AGC UI and cite the exact
source/date in the report. The workshop version metadata is inconsistent
(`SKILL.md` says 6.1.0 while `_meta.json` says 5.0.0); do not infer API or policy
support from that inconsistency.

## Guardrails

- Do not log, copy, upload, install, generate, or expose signing secrets.
- Do not perform AGC login/upload, certificate creation, publication, commit,
  push, deletion, dependency installation, or deployment without explicit user
  authorization.
- Do not claim “审核通过” from static code inspection, a successful debug
  build, or an unverified screenshot. Distinguish build success from signed
  release readiness and from AGC approval.
- Do not invent official thresholds, required permissions, API behavior, or
  hidden workshop material. Mark uncertain rules `UNVERIFIED` and suggest
  checking the current official Huawei AppGallery documentation or AGC console.
- Preserve unrelated working-tree changes. Never rewrite a user's signing
  configuration just to make a scanner pass.
- Ask before destructive, external, installation, publication, commit, or push actions.
- Do not use secrets, local absolute paths, or undocumented private interfaces.

## Validation

For this Skill package, validate the helper script and check for obvious issues:

```bash
# Run the preflight checker against a fixture
python3 scripts/check_harmony_release.py --project-root <project-root> --format text

# Run unit tests
python3 -m unittest discover -s tests -p 'test_*.py'

# Quick smoke test with --strict and --forbid-network
python3 scripts/check_harmony_release.py --project-root <project-root> --forbid-network --strict --format json
```

When validating against the actual Harmony Wardrobe project, also run the
repository-level checks listed in the project's AGENTS.md.

## References

- Read `references/harmonyos-appgallery-self-check.md` before producing a full
  report; it contains the check IDs, workshop baseline mapping, and the
  Harmony Wardrobe evidence map.
- Read only the relevant reference sections for focused checks. Keep current
  official AGC/Huawei documentation above the workshop-derived baseline.
