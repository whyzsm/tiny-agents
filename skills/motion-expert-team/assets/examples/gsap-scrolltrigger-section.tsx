'use client';

import { useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, useGSAP);

export function ProductStorySection() {
  const scope = useRef<HTMLElement | null>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();

      mm.add('(prefers-reduced-motion: no-preference)', () => {
        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: scope.current,
            start: 'top top',
            end: '+=180%',
            scrub: 1,
            pin: true,
            anticipatePin: 1,
          },
        });

        tl.from('[data-step="1"]', { autoAlpha: 0, y: 40, duration: 0.6 })
          .to('[data-visual]', { scale: 1.06, ease: 'none', duration: 1 }, '<')
          .from('[data-step="2"]', { autoAlpha: 0, y: 40, duration: 0.6 }, '+=0.15');
      });

      mm.add('(prefers-reduced-motion: reduce)', () => {
        gsap.set('[data-step], [data-visual]', { clearProps: 'all', autoAlpha: 1, y: 0, scale: 1 });
      });

      return () => mm.revert();
    },
    { scope }
  );

  return (
    <section ref={scope} data-story>
      <div data-visual aria-hidden="true" />
      <div data-step="1">First product point</div>
      <div data-step="2">Second product point</div>
    </section>
  );
}
