# Motion Review Rubric

Use this for code review, design critique, or implementation QA.

## Ship verdicts

| Verdict | Meaning |
|---|---|
| Ship | Motion has clear intent, safe implementation, reduced-motion support, no notable performance risks. |
| Ship with nits | Safe to merge; minor timing/easing/choreography refinements remain. |
| Fix before ship | User-visible or engineering issue: reduced-motion gap, cleanup issue, library misuse, performance risk. |
| Redesign motion | Motion intent, stack choice, or interaction model is wrong; patching code is insufficient. |

## Review output format

```text
Ship verdict:
Intent verdict:
Library fit:
Critical issues:
Performance risks:
Accessibility/reduced-motion:
Patch suggestions:
```

For code review:

| Severity | Snippet | Why it matters | Concrete fix |
|---|---|---|---|
| Blocker | quote line/snippet | one sentence | exact code-level suggestion |

## Severity scale

### Blocker

- No reduced-motion behavior for significant motion.
- Continuous layout animation or layout thrashing.
- Raw scroll polling drives animation.
- GSAP/ScrollTrigger not cleaned up in React.
- Animation delays keyboard or focus behavior.
- Infinite RAF/timer loop with no stop condition.

### High

- Wrong library for the job.
- Mixed animation systems in same component without boundary.
- Large paint/filter/backdrop animation.
- Non-interruptible interaction.
- Overly long motion blocking user action.

### Medium

- Inconsistent timing/easing.
- Excessive stagger.
- Motion direction conflicts with spatial model.
- Ambiguous transform origin.
- Missing mobile simplification.

### Polish

- Better curve choice.
- Slight duration adjustment.
- Cleaner choreography.
- Naming/token improvements.

## Design review prompts

Ask these internally:

1. Does the motion communicate state or just decorate?
2. Would the UI still make sense with motion disabled?
3. Does the element move from/to where the user expects?
4. Does the motion respect interaction frequency?
5. Is the sequence legible, or are too many things moving at once?
6. Does the chosen library match the complexity?
7. Are transform/opacity sufficient?
8. Are scroll and cleanup handled by the library, not manual event math?

## Patch style

When fixing code:

- Keep the existing stack.
- Change the fewest files needed.
- Preserve semantics and focus behavior.
- Add reduced-motion support in the same patch.
- Explain non-obvious motion choices briefly.
- Prefer code diffs or complete replacement snippets.
