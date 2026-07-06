# HarmonyOS Ask Checklist

Use this for project-aware Q&A, explanations, and troubleshooting.

## Inspect When Relevant

- `module.json5`: abilities, extension abilities, permissions, metadata, skills.
- `main_pages.json`: page registration and route names.
- `build-profile.json5`: compile SDK, products, signing, modules.
- `oh-package.json5`: dependencies and scripts.
- Nearby `.ets`, `.ts`, `.json5`, resource files: local conventions and existing patterns.

## Common Topics

- ArkUI state: `@State`, `@Prop`, `@Link`, `@Provide`, `@Consume`, `@Observed`, `@ObjectLink`, `AppStorage`, `PersistentStorage`.
- Lifecycle: `aboutToAppear`, `aboutToDisappear`, page show/hide hooks.
- Navigation: route string consistency, parameter passing, page registration.
- Permissions: config declaration plus runtime authorization where required.
- Performance: lazy lists, avoiding redundant state writes, async work outside UI hot paths.
- Build: hvigor, module boundaries, dependency availability, JSON5 syntax.

## Answer Shape

- Start with the direct answer.
- Add project-specific evidence or assumptions.
- Give a minimal code/config example only when helpful.
- Finish with targeted verification steps if the user is debugging.
