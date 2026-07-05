# ArkUI Page Generation Checklist

Use this before and after generating HarmonyOS UI code.

## Inputs To Clarify Or Infer

- Target module and page/component name.
- Device class and orientation assumptions.
- Data source: static sample data, local state, existing store, or API.
- Primary interactions and navigation destinations.
- Required states: loading, empty, error, disabled, selected, long content.

## Files To Inspect

- Existing `.ets` pages/components in the same module.
- `main_pages.json` or local route registry.
- Resource files under `resources/*/element` and `resources/*/media`.
- `module.json5` if system capability, ability, or metadata changes are needed.

## ArkUI Implementation Checks

- Use declarative components and local project conventions.
- Keep state ownership minimal and clear.
- Ensure repeated items have stable layout and list/grid rendering.
- Avoid text overlap by allowing wrap/ellipsis according to context.
- Use resources when the project already localizes strings or centralizes colors.
- Register new routes exactly once.

## Verification Checks

- Imports resolve.
- Decorators and component names are valid.
- JSON5 config remains valid.
- New pages are reachable.
- UI states do not resize controls unexpectedly.
