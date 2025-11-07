'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface BorderTrailProps {
  className?: string
  size?: number
  color?: string
  duration?: number
  delay?: number
  children?: React.ReactNode
}

export function BorderTrail({
  className,
  size = 200,
  color = '#eab308',
  duration = 3,
  delay = 0,
  children,
}: BorderTrailProps) {
  return (
    <div className={cn('relative inline-block', className)}>
      {/* Animated Border Trail */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        style={{ filter: 'drop-shadow(0 0 8px currentColor)' }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          cx="50%"
          cy="50%"
          r={`calc(50% - 6px)`}
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray="10 200"
          opacity="0.7"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 50% 50%"
            to="360 50% 50%"
            dur={`${duration}s`}
            repeatCount="indefinite"
            begin={`${delay}s`}
          />
        </circle>
        <circle
          cx="50%"
          cy="50%"
          r={`calc(50% - 6px)`}
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray="10 200"
          opacity="0.4"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="360 50% 50%"
            to="0 50% 50%"
            dur={`${duration * 1.5}s`}
            repeatCount="indefinite"
            begin={`${delay}s`}
          />
        </circle>
      </svg>

      {/* Glow effect */}
      <motion.div
        className="absolute inset-0 rounded-full blur-xl opacity-50"
        style={{ backgroundColor: color }}
        animate={{
          opacity: [0.3, 0.6, 0.3],
          scale: [0.95, 1.05, 0.95],
        }}
        transition={{
          duration: duration,
          repeat: Infinity,
          delay: delay,
        }}
      />

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  )
}
