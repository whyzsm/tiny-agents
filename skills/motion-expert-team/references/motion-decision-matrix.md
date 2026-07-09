# Motion Decision Matrix

Use this before writing animation code.

## 1. Why should it move?

| Intent | Good motion | Bad motion |
|---|---|---|
| Feedback | Press compresses, success confirms, error gently shakes or highlights | Decorative bounce on every click |
| Orientation | Drawer emerges from edge; dropdown opens from trigger | Generic center pop for every overlay |
| Continuity | Shared element keeps identity across states | Element disappears and reappears somewhere else |
| Hierarchy | Important content enters first; secondary content follows | Everything animates at once or with random stagger |
| Narrative | Scroll reveals product steps in a controlled sequence | Parallax unrelated to content meaning |
| Brand | Motion matches product personality | Random spring curves copied from another app |
| Delight | Rare celebration, completion, empty-state charm | Frequent confetti, excessive wobble, delayed productivity actions |

If no intent is defensible, keep it static.

## 2. Pick the smallest sufficient stack

| Requirement | Use | Avoid |
|---|---|---|
| Button, hover, opacity, simple translate | CSS transition | JS animation library |
| Mount/unmount with simple state | CSS `@starting-style`, data-state, Motion if already present | layout properties |
| React component variants | `motion/react` | ad-hoc RAF |
| Drag/swipe/gesture | Motion/Framer or existing gesture system | CSS-only hacks that break input |
| Sequenced hero timeline | GSAP timeline | long chains of CSS delays |
| Scroll pinning/scrub/horizontal | GSAP ScrollTrigger | manual scroll event math |
| In-view reveal | Motion `whileInView`, IntersectionObserver + CSS, or GSAP if already used | polling `scrollY` |
| Authored illustration/logo | Lottie/dotLottie | DOM animating a complex vector by hand |
| Layout-like transition | FLIP or native layout animation | continuous `width`/`height`/`top`/`left` animation |

## 3. Timing defaults

| Surface | Duration | Notes |
|---|---:|---|
| Repetitive control feedback | 100–160ms | Must feel immediate |
| Hover / focus-visible visual change | 150–220ms | Focus behavior itself must not be delayed |
| Small popover / tooltip | 125–200ms | Keep close to trigger |
| Dropdown / select / command menu | 150–250ms | Use transform-origin from trigger |
| Modal / drawer / sheet | 200–350ms | Larger surfaces can take longer |
| Page / route transition | 250–450ms | Keep perceived speed high |
| Marketing section entrance | 500–900ms | Use only when it supports storytelling |
| Long narrative / hero reveal | 600–1200ms | Rare; avoid blocking interaction |

## 4. Easing defaults

| Use case | Curve |
|---|---|
| Enter / reveal | `cubic-bezier(0.22, 1, 0.36, 1)` |
| Move / slide | `cubic-bezier(0.25, 1, 0.5, 1)` |
| Exit / dismiss | `cubic-bezier(0.4, 0, 1, 1)` |
| Simple color/opacity | `ease` |
| Scroll scrub | `linear` / GSAP `ease: 'none'` |
| Playful rare delight | spring with low overshoot; never on high-frequency controls |

## 5. Motion personality presets

| Personality | Duration bias | Easing | Use for |
|---|---|---|---|
| Calm / enterprise | Slightly shorter | Subtle ease-out | SaaS dashboards, admin tools |
| Premium | Medium | Smooth custom ease, subtle stagger | Landing pages, luxury/product marketing |
| Playful | Short-to-medium | Gentle spring, small overshoot | Onboarding, empty states, creation tools |
| Technical | Short | Precise, linear or restrained ease | Developer tools, data products |
| Energetic | Short, snappy | Punchy ease-out | Consumer apps, launches, celebration moments |

## 6. Choreography rules

- Animate from most important to least important.
- Stagger small lists by 40–100ms; avoid long cascading delays.
- Do not stagger huge lists. Animate the container or virtualized rows only.
- Shared/persistent elements should move in place.
- Large surfaces should move less than small details.
- Exit should usually be faster than entrance.
- The user should never wait for motion before they can act, unless motion is the content.
