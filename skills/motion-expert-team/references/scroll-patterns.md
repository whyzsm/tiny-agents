# Scroll Patterns

Use this when the user asks for scroll animation, parallax, pinned sections, scrubbed timelines, reveal-on-scroll, horizontal scroll, progress bars, or Apple-like product storytelling.

## Stack selector

| Need | Prefer |
|---|---|
| Vanilla JS, Webflow, Vue, complex timelines | GSAP ScrollTrigger |
| React/Next declarative in-view reveal | `motion/react` `whileInView` |
| React/Next scroll-linked value transforms | `motion/react` `useScroll` + `useTransform` |
| Pinning, scrub, snapping, horizontal scroll | GSAP ScrollTrigger |
| Existing app already uses GSAP | GSAP |
| Existing app already uses Motion/Framer and effect is simple | Motion/Framer |

Do not introduce both GSAP and Motion into the same component unless there is a clear boundary and the user accepts the complexity.

## GSAP setup

```ts
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);
```

React setup:

```tsx
'use client';

import { useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, useGSAP);
```

## GSAP reveal-on-scroll

```ts
gsap.from('[data-reveal]', {
  autoAlpha: 0,
  y: 40,
  duration: 0.7,
  ease: 'power2.out',
  stagger: 0.08,
  scrollTrigger: {
    trigger: '[data-reveal-root]',
    start: 'top 80%',
    once: true,
  },
});
```

## GSAP scrubbed parallax

```ts
gsap.to('[data-parallax]', {
  yPercent: -16,
  ease: 'none',
  scrollTrigger: {
    trigger: '[data-parallax-root]',
    start: 'top bottom',
    end: 'bottom top',
    scrub: true,
  },
});
```

Use `ease: 'none'` for scrubbed animation.

## GSAP pinned timeline

```ts
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '[data-story]',
    start: 'top top',
    end: '+=200%',
    pin: true,
    scrub: 1,
    anticipatePin: 1,
  },
});

tl.from('[data-step="1"]', { autoAlpha: 0, y: 40 })
  .to('[data-visual]', { scale: 1.08, ease: 'none' })
  .from('[data-step="2"]', { autoAlpha: 0, y: 40 });
```

## Motion/Framer in-view reveal

```tsx
'use client';

import { motion, useReducedMotion } from 'motion/react';

export function Reveal({ children }: { children: React.ReactNode }) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 32 }}
      whileInView={reduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: reduceMotion ? 0.12 : 0.5, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

## Motion/Framer scroll-linked transform

```tsx
'use client';

import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react';

export function ParallaxLayer() {
  const ref = useRef<HTMLDivElement | null>(null);
  const reduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
  const y = useTransform(scrollYProgress, [0, 1], reduceMotion ? [0, 0] : [40, -40]);

  return <motion.div ref={ref} style={{ y }} />;
}
```

## Scroll review checklist

- Is scroll motion tied to content meaning?
- Does it use a library-native scroll mechanism instead of raw polling?
- Is reduced motion handled?
- Are only transform/opacity animated during scroll?
- Are ScrollTriggers cleaned up on unmount?
- Are markers removed before production?
- Is pinning necessary, and is the pinned duration reasonable?
- Does mobile get a simpler pattern when needed?
