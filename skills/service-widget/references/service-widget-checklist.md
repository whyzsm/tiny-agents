# Service Widget Checklist

Use this for HarmonyOS service widget/card work.

## Files And Areas To Inspect

- Existing widget/card source files in the target module.
- `resources/*/profile/form_config.json` or equivalent widget config.
- `module.json5` for ability, extension ability, metadata, and permissions.
- Resource folders for strings, colors, dimensions, media, and layered images.
- Build files and package dependencies.

## Widget Definition

- Widget name starts with a letter and uses only letters, digits, and underscores.
- Name does not conflict with existing files/config entries.
- Size and layout match the requested widget type.
- Display data and interactions are clear.
- Refresh/update behavior is explicit or follows the existing project pattern.

## Implementation Checks

- Layout code, logic code, resources, and config entries are added together.
- Resource references match actual files.
- JSON/JSON5 syntax is valid.
- Config references point to the correct ability/component.
- Long text truncates or wraps appropriately for widget size.

## Verification Checks

- Project build/check command runs if available.
- Preview/save flow has no missing file paths.
- Generated files fit module conventions and do not use absolute local paths.
