# HarmonyOS Project Checklist

Use this reference when implementation touches project structure, ArkTS UI, permissions, lifecycle, or build configuration.

## Project Files

- `app.json5`: application-level identity such as bundle name, vendor, version code, and version name.
- `module.json5`: module type, abilities, skills, metadata, extension abilities, and requested permissions.
- `main_pages.json`: page route registry. New pages usually need an entry here or in the project’s equivalent route registry.
- `build-profile.json5`: app/module build settings, products, compile SDK, signing, and included modules.
- `hvigorfile.ts`: build task wiring.
- `oh-package.json5`: dependencies and project package metadata.

## ArkTS And ArkUI Checks

- Match existing decorators and state ownership:
  - `@State` for local mutable UI state.
  - `@Prop` for parent-to-child values.
  - `@Link` for two-way parent-child state.
  - `@Provide` / `@Consume` for scoped dependency sharing.
  - `@Observed` / `@ObjectLink` for observable object graphs.
  - `AppStorage` or `PersistentStorage` only when cross-page/global or persisted state is required.
- Keep component lifecycle work intentional:
  - Initialize or refresh view data in `aboutToAppear` only when tied to component visibility.
  - Release timers, subscriptions, and listeners in `aboutToDisappear`.
  - Use page lifecycle hooks for page visibility, not general component setup.
- Prefer existing resource usage for strings, colors, dimensions, and media.
- Check neighboring `.ets` files before choosing layout, naming, imports, and error handling style.

## Navigation And Pages

- When adding a page, create the `.ets` file and register the route in `main_pages.json` or the local router map.
- Verify route strings match exactly between navigation calls and route registration.
- For parameter passing, follow the project’s existing router parameter pattern.

## Permissions And System APIs

- Before adding a permission, confirm the HarmonyOS API requires it.
- Add only the specific permission needed in `module.json5`.
- Check whether the API also requires runtime authorization, user consent, or metadata.

## Build And Verification

- Inspect the repo for the preferred command before building:
  - wrapper scripts such as `hvigorw`
  - `oh-package.json5` scripts or project documentation
  - existing CI/build scripts
- If a full build is too slow or unavailable, run targeted checks and inspect changed imports/configs manually.
- After edits, verify:
  - changed `.ets` files have valid imports and decorators
  - new pages are registered
  - new resources are referenced correctly
  - permissions/config changes are minimal
  - no unrelated files were reformatted
