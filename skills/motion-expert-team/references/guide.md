# Motion 动效专家团指南

This guide routes UI motion work across design intent, implementation stack choice, scroll animation, GSAP correctness, performance, and accessibility.

## Source Composition

This expert team is converted from the local `motion-expert-agent` package. It synthesizes five public motion-skill roles without vendoring full upstream skills:

| Module | Role |
|---|---|
| `motion-direction` | Define why motion exists: feedback, orientation, continuity, hierarchy, narrative, brand, or rare delight. |
| `ui-animation-implementation` | Implement CSS, Motion/Framer, springs, gestures, component states, and accessible interaction patterns. |
| `scroll-animation-patterns` | Handle reveal-on-scroll, parallax, pinned sections, scrubbed timelines, horizontal scroll, and product storytelling. |
| `gsap-animation-expertise` | Use GSAP timelines, ScrollTrigger, plugins, React cleanup, selectors, and performance patterns correctly. |
| `motion-performance-review` | Prevent layout thrashing, scroll jank, expensive paints, permanent `will-change`, uncontrolled RAF, and reduced-motion failures. |

## Request Routing

- For motion concept, choreography, duration, easing, or whether something should animate: read `motion-decision-matrix.md`.
- For CSS, Motion/Framer, GSAP, Lottie, FLIP, or mixed-stack implementation: start with the stack selector in `motion-decision-matrix.md`.
- For scroll motion, parallax, pinning, scrubbed animation, horizontal scroll, or in-view reveal: read `scroll-patterns.md`.
- For jank, Core Web Vitals risk, layout thrashing, paint-heavy effects, or cleanup failures: read `performance-guardrails.md`.
- For animation code review or design critique: read `review-rubric.md`.
- For quick implementation templates, adapt the examples in `assets/examples/`.

## Motion Spec

For non-trivial work, infer or output:

```text
Intent:
Element(s):
Trigger:
Library/technique:
Duration:
Easing/spring:
Direction/origin:
Sequence/stagger:
Reduced-motion behavior:
Performance risks:
```

## Stack Selection

- CSS: simple hover, press, opacity, translate, tiny feedback, DOM entry with `@starting-style`.
- Motion/Framer: React or Next component states, variants, gestures, simple in-view reveals, scroll transforms.
- GSAP: timelines, ScrollTrigger, pinning, scrubbed scroll, horizontal scroll, complex choreography.
- Lottie/dotLottie: authored illustration, logo, and brand animation.
- FLIP: layout-like transitions that must preserve object identity.

Respect the existing project stack. Do not migrate animation libraries unless the user explicitly asks.

## Review Format

```text
Ship verdict: Ship | Ship with nits | Fix before ship | Redesign motion
Intent verdict:
Library fit:
Critical issues:
Performance risks:
Accessibility/reduced-motion:
Patch suggestions:
```

## Conversion Notes

- This is a repository-only converted expert team.
- Do not run `install-upstream-skills.sh`.
- Do not copy Cursor, Copilot, or local installation configuration into target projects unless explicitly requested.
- Source examples are reusable templates, not mandatory project structure.
