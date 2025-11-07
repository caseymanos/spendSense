'use client'

import * as React from 'react'
import { motion, useSpring, useTransform, animate } from 'framer-motion'
import { cn } from '@/lib/utils'

export interface CounterTextProps {
  value: number
  decimals?: number
  duration?: number
  prefix?: string
  suffix?: string
  className?: string
  onComplete?: () => void
}

export function CounterText({
  value,
  decimals = 0,
  duration = 1,
  prefix = '',
  suffix = '',
  className,
  onComplete,
}: CounterTextProps) {
  const [displayValue, setDisplayValue] = React.useState(0)
  const prevValue = React.useRef(0)

  React.useEffect(() => {
    const controls = animate(prevValue.current, value, {
      duration,
      ease: 'easeOut',
      onUpdate(latest) {
        setDisplayValue(latest)
      },
      onComplete,
    })

    prevValue.current = value

    return () => controls.stop()
  }, [value, duration, onComplete])

  const formattedValue = displayValue.toFixed(decimals)

  return (
    <motion.span
      className={cn('tabular-nums', className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {prefix}
      {formattedValue}
      {suffix}
    </motion.span>
  )
}

/**
 * Animates number changes with spring physics
 */
export function SpringCounterText({
  value,
  decimals = 0,
  prefix = '',
  suffix = '',
  className,
}: Omit<CounterTextProps, 'duration' | 'onComplete'>) {
  const spring = useSpring(value, { stiffness: 100, damping: 30 })
  const display = useTransform(spring, (current) =>
    `${prefix}${current.toFixed(decimals)}${suffix}`
  )

  React.useEffect(() => {
    spring.set(value)
  }, [spring, value])

  return (
    <motion.span
      className={cn('tabular-nums', className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {display}
    </motion.span>
  )
}
