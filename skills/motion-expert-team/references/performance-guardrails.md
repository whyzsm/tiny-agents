# Motion Performance Guardrails

Use this for implementation and review.

## Render cost model

| Category | Typical properties | Cost |
|---|---|---|
| Composite | `transform`, `opacity` | Cheapest; default for motion |
| Paint | `color`, `background`, `box-shadow`, `filter`, `mask`, gradients | Use on small isolated surfaces only |
| Layout | `width`, `height`, `top`, `left`, margins, padding, grid/flex placement | Avoid continuous animation |

## Blocker rules

The agent must block or rewrite code that does these:

1. Interleaves layout reads and writes in the same frame.
2. Animates layout properties continuously on meaningful surfaces.
3. Drives animation from raw `scrollTop`, `scrollY`, or unthrottled scroll events.
4. Uses `requestAnimationFrame` loops without stop conditions.
5. Mixes multiple animation systems that each mutate/measure layout in the same component.
6. Uses `transition: all`.
7. Leaves broad or permanent `will-change` in production.
8. Animates large blur/filter/backdrop-filter surfaces continuously.
9. Ships no reduced-motion path.

## Safer replacements

| Problem | Safer replacement |
|---|---|
| `width`/`height` animation | `transform: scaleX/scaleY`, clip wrapper, or FLIP |
| `top`/`left` animation | `transform: translate(...)` |
| Scroll event sets style every tick | CSS scroll/view timeline, GSAP ScrollTrigger, Motion `useScroll`, or IntersectionObserver |
| Large shadow/blur animation | Opacity/translate; static shadow; tiny one-shot blur only |
| Repeated `getBoundingClientRect()` in animation | Measure once before animation; batch reads before writes |
| Many row animations | Animate container; limit stagger; virtualize; reveal only visible batch |
| Permanent `will-change` | Add shortly before animation, remove on completion |
| Complex layout change | FLIP transition |

## FLIP checklist

1. First: measure initial rects.
2. Last: apply final layout state and measure final rects.
3. Invert: apply transform from delta.
4. Play: animate transform back to identity.
5. Cleanup: remove inline transforms/transitions.

## Scroll performance rules

- For GSAP ScrollTrigger: register plugin once, scope selectors, clean up on unmount, remove markers before production.
- For scrubbed animations: use no easing (`ease: 'none'`) so motion tracks scroll.
- Prefer one parent ScrollTrigger timeline over many independent triggers for related elements.
- Pause or skip non-visible continuous animations.
- Avoid scroll-linked filter, backdrop-filter, box-shadow, large gradient, and layout changes.
- Refresh ScrollTrigger only after real layout changes, not in every render.

## Layer rules

- Layer promotion is useful but not free.
- Use `will-change` surgically on elements that are about to animate.
- Avoid promoting many or huge elements.
- Remove `will-change` after the animation finishes.
- Validate with browser performance tooling when the surface is large or important.

## Blur and filter rules

- Default: avoid filter animation for core interactions.
- If used, keep blur small, short, and one-shot.
- Treat blur above 8px as a special-case visual effect requiring justification.
- Never animate blur continuously on large surfaces.
- Prefer opacity and transform first.

## Reduced-motion performance path

Reduced motion is also a performance path. For users who request it:

- Skip scroll scrubbing, parallax, and continuous ambient loops.
- Replace spatial motion with opacity or instant state changes.
- Keep status and orientation clear without relying on movement.
