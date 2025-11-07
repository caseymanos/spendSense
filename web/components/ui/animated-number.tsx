'use client'

import React, { useEffect, useRef, useState } from 'react'
import { motion, useInView, useSpring, useTransform } from 'framer-motion'

interface AnimatedNumberProps {
  value: number
  duration?: number
  decimals?: number
  prefix?: string
  suffix?: string
  className?: string
  delay?: number
}

export function AnimatedNumber({
  value,
  duration = 2,
  decimals = 0,
  prefix = '',
  suffix = '',
  className = '',
  delay = 0,
}: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })
  const [displayValue, setDisplayValue] = useState(0)

  // Create animated spring value
  const spring = useSpring(0, {
    duration: duration * 1000,
    bounce: 0,
  })

  useEffect(() => {
    if (isInView) {
      // Add delay before animation starts
      const timeout = setTimeout(() => {
        spring.set(value)
      }, delay * 1000)

      return () => clearTimeout(timeout)
    }
  }, [isInView, value, spring, delay])

  useEffect(() => {
    const unsubscribe = spring.on('change', (latest) => {
      setDisplayValue(latest)
    })

    return () => unsubscribe()
  }, [spring])

  const formattedValue = displayValue.toFixed(decimals)

  return (
    <motion.span
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.5, delay: delay }}
    >
      {prefix}
      {formattedValue}
      {suffix}
    </motion.span>
  )
}

export function SlidingNumber({
  value,
  className = '',
  decimals = 0,
}: {
  value: number
  className?: string
  decimals?: number
}) {
  const digits = value.toFixed(decimals).split('')

  return (
    <span className={className}>
      {digits.map((digit, index) => (
        <motion.span
          key={index}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{
            duration: 0.5,
            delay: index * 0.05,
            ease: [0.33, 1, 0.68, 1],
          }}
          className="inline-block"
        >
          {digit}
        </motion.span>
      ))}
    </span>
  )
}
