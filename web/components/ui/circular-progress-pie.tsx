'use client'

import React, { useEffect, useState } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'
import { cn } from '@/lib/utils'

interface CircularProgressPieProps {
  value: number
  size?: number
  strokeWidth?: number
  color?: string
  backgroundColor?: string
  showGradient?: boolean
  showShadow?: boolean
  animationDuration?: number
  children?: React.ReactNode
  className?: string
}

export function CircularProgressPie({
  value,
  size = 200,
  strokeWidth = 12,
  color = '#eab308',
  backgroundColor = '#e5e7eb',
  showGradient = true,
  showShadow = true,
  animationDuration = 2,
  children,
  className,
}: CircularProgressPieProps) {
  const [mounted, setMounted] = useState(false)

  // Calculate circle properties
  const center = size / 2
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius

  // Animated progress value
  const progress = useSpring(0, {
    duration: animationDuration * 1000,
    bounce: 0,
  })

  // Transform progress to stroke dashoffset
  const strokeDashoffset = useTransform(
    progress,
    [0, 100],
    [circumference, 0]
  )

  useEffect(() => {
    setMounted(true)
    const timer = setTimeout(() => {
      progress.set(value)
    }, 100)
    return () => clearTimeout(timer)
  }, [value, progress])

  const gradientId = `circular-gradient-${Math.random().toString(36).substr(2, 9)}`
  const shadowId = `circular-shadow-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div className={cn('relative inline-block', className)} style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="transform -rotate-90"
      >
        <defs>
          {/* Gradient definition */}
          {showGradient && (
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity={1} />
              <stop offset="50%" stopColor={color} stopOpacity={0.8} />
              <stop offset="100%" stopColor={color} stopOpacity={1} />
            </linearGradient>
          )}

          {/* Drop shadow filter */}
          {showShadow && (
            <filter id={shadowId} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
              <feOffset dx="0" dy="2" result="offsetblur" />
              <feComponentTransfer>
                <feFuncA type="linear" slope="0.3" />
              </feComponentTransfer>
              <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          )}
        </defs>

        {/* Background circle (track) */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          opacity={0.2}
        />

        {/* Animated progress circle (pie) */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke={showGradient ? `url(#${gradientId})` : color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          filter={showShadow ? `url(#${shadowId})` : undefined}
          style={{
            transformOrigin: 'center',
          }}
        />

        {/* Inner glow ring */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius - strokeWidth / 2}
          fill="none"
          stroke={color}
          strokeWidth={2}
          opacity={0.3}
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{
            scale: mounted ? [0.95, 1, 0.95] : 0.95,
            opacity: mounted ? [0.2, 0.4, 0.2] : 0,
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        {/* Outer glow ring */}
        <motion.circle
          cx={center}
          cy={center}
          r={radius + strokeWidth / 2}
          fill="none"
          stroke={color}
          strokeWidth={2}
          opacity={0.2}
          initial={{ scale: 1, opacity: 0 }}
          animate={{
            scale: mounted ? [1, 1.05, 1] : 1,
            opacity: mounted ? [0.1, 0.3, 0.1] : 0,
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1.5,
          }}
        />

        {/* Radial segments (pie chart effect) */}
        {[0, 90, 180, 270].map((angle, index) => (
          <motion.line
            key={angle}
            x1={center}
            y1={center}
            x2={center + radius * Math.cos((angle * Math.PI) / 180)}
            y2={center + radius * Math.sin((angle * Math.PI) / 180)}
            stroke={color}
            strokeWidth={0.5}
            opacity={0.15}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: mounted ? 1 : 0 }}
            transition={{
              duration: 1,
              delay: index * 0.1,
              ease: 'easeOut',
            }}
          />
        ))}

      </svg>

      {/* Content overlay */}
      <div className="absolute inset-0 flex items-center justify-center">
        {children}
      </div>

      {/* Rotating shimmer effect */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background: `conic-gradient(from 0deg, transparent 0%, ${color}20 50%, transparent 100%)`,
          mixBlendMode: 'overlay',
        }}
        animate={{
          rotate: mounted ? 360 : 0,
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'linear',
        }}
      />
    </div>
  )
}
