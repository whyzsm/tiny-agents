'use client';

import { motion, useReducedMotion } from 'motion/react';

type MotionCardProps = {
  children: React.ReactNode;
  index?: number;
};

export function MotionCard({ children, index = 0 }: MotionCardProps) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.article
      initial={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 16 }}
      animate={reduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }}
      transition={{
        duration: reduceMotion ? 0.12 : 0.24,
        delay: reduceMotion ? 0 : Math.min(index * 0.04, 0.24),
        ease: [0.22, 1, 0.36, 1],
      }}
      whileHover={reduceMotion ? undefined : { y: -2 }}
    >
      {children}
    </motion.article>
  );
}
