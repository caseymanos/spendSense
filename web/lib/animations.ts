/**
 * Animation Variants Library for Framer Motion
 * Provides reusable animation patterns for consistent UI interactions
 */

import { Variants } from 'framer-motion'

/**
 * Fade in without movement
 * Perfect for: Cards, sections, modals appearing
 */
export const fadeInUp: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.46, 0.45, 0.94], // easeOutQuad
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.3,
    },
  },
}

/**
 * Fade in with no movement
 * Perfect for: Overlays, backgrounds
 */
export const fadeIn: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.4,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
}

/**
 * Scale and fade in (pop effect)
 * Perfect for: Buttons, badges, interactive elements
 */
export const scaleIn: Variants = {
  initial: {
    opacity: 0,
    scale: 0.8,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: [0.34, 1.56, 0.64, 1], // easeOutBack
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: {
      duration: 0.2,
    },
  },
}

/**
 * Slide in from left
 * Perfect for: Side panels, drawers, list items
 */
export const slideInLeft: Variants = {
  initial: {
    opacity: 0,
    x: -40,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  },
  exit: {
    opacity: 0,
    x: -40,
    transition: {
      duration: 0.3,
    },
  },
}

/**
 * Stagger children animation
 * Perfect for: Lists, grids, multiple items appearing sequentially
 */
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
}

/**
 * Fast stagger for dense grids
 */
export const staggerContainerFast: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
}

/**
 * Hover scale up effect
 * Perfect for: Interactive cards, buttons
 */
export const hoverScale = {
  rest: { scale: 1 },
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: 'easeInOut',
    },
  },
  tap: {
    scale: 0.98,
  },
}

/**
 * Subtle hover glow effect
 * Perfect for: Cards, panels
 */
export const hoverLift = {
  rest: {
    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    transition: {
      duration: 0.2,
    },
  },
  hover: {
    boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    transition: {
      duration: 0.2,
      ease: 'easeOut',
    },
  },
}

/**
 * Pulse animation for attention-grabbing elements
 * Perfect for: Notifications, badges, alerts
 */
export const pulse: Variants = {
  initial: { scale: 1 },
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

/**
 * Shimmer loading effect
 * Perfect for: Skeleton screens, loading states
 */
export const shimmer = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
}

/**
 * Number counter animation
 * Perfect for: Stats, metrics, counters
 */
export const counterVariants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut',
    },
  },
}

/**
 * Blur in effect for glass morphism
 * Perfect for: Modal overlays, glass cards appearing
 */
export const blurIn: Variants = {
  initial: {
    opacity: 0,
    backdropFilter: 'blur(0px)',
  },
  animate: {
    opacity: 1,
    backdropFilter: 'blur(20px)',
    transition: {
      duration: 0.5,
    },
  },
  exit: {
    opacity: 0,
    backdropFilter: 'blur(0px)',
    transition: {
      duration: 0.3,
    },
  },
}

/**
 * Rotate and scale for badges
 * Perfect for: Priority badges, status indicators
 */
export const rotateBadge: Variants = {
  initial: {
    opacity: 0,
    scale: 0.5,
    rotate: -10,
  },
  animate: {
    opacity: 1,
    scale: 1,
    rotate: 0,
    transition: {
      duration: 0.6,
      ease: [0.34, 1.56, 0.64, 1],
    },
  },
}

/**
 * Expand width animation
 * Perfect for: Progress bars, expanding panels
 */
export const expandWidth: Variants = {
  initial: {
    width: 0,
    opacity: 0,
  },
  animate: {
    width: '100%',
    opacity: 1,
    transition: {
      duration: 0.8,
      ease: 'easeOut',
    },
  },
}

/**
 * Scroll-triggered reveal without movement
 * Perfect for: Sections appearing on scroll
 */
export const scrollReveal: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.6,
      ease: [0.25, 0.46, 0.45, 0.94],
    },
  },
}

/**
 * Spring bounce effect
 * Perfect for: Playful interactions, confirmations
 */
export const springBounce: Variants = {
  initial: { scale: 0 },
  animate: {
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 260,
      damping: 20,
    },
  },
}

/**
 * Gentle pulse animation (continuous)
 * Perfect for: Badges, icons - no vertical movement
 */
export const gentleFloat = {
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
}

/**
 * Path drawing animation for SVGs
 * Perfect for: Check marks, icons, illustrations
 */
export const drawPath = {
  initial: {
    pathLength: 0,
    opacity: 0,
  },
  animate: {
    pathLength: 1,
    opacity: 1,
    transition: {
      duration: 1,
      ease: 'easeInOut',
    },
  },
}

/**
 * Preset transition configurations
 */
export const transitions = {
  default: {
    duration: 0.3,
    ease: [0.25, 0.46, 0.45, 0.94],
  },
  fast: {
    duration: 0.15,
    ease: 'easeInOut',
  },
  slow: {
    duration: 0.6,
    ease: [0.25, 0.46, 0.45, 0.94],
  },
  spring: {
    type: 'spring' as const,
    stiffness: 300,
    damping: 30,
  },
  springGentle: {
    type: 'spring' as const,
    stiffness: 200,
    damping: 25,
  },
  springBouncy: {
    type: 'spring' as const,
    stiffness: 400,
    damping: 20,
  },
}
