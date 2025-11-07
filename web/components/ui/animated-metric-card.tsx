'use client'

import * as React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { fadeInUp, scaleIn } from '@/lib/animations'

export interface AnimatedMetricCardProps {
  label: string
  value: string | number
  suffix?: string
  description?: string
  icon?: React.ReactNode
  variant?: 'blue' | 'purple' | 'emerald' | 'rose' | 'amber' | 'orange'
  className?: string
  delay?: number
}

const variantClasses = {
  blue: 'from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/50 text-blue-600 dark:text-blue-400',
  purple: 'from-purple-50 to-purple-100 dark:from-purple-950/50 dark:to-purple-900/50 text-purple-600 dark:text-purple-400',
  emerald: 'from-emerald-50 to-emerald-100 dark:from-emerald-950/50 dark:to-emerald-900/50 text-emerald-600 dark:text-emerald-400',
  rose: 'from-rose-50 to-rose-100 dark:from-rose-950/50 dark:to-rose-900/50 text-rose-600 dark:text-rose-400',
  amber: 'from-amber-50 to-amber-100 dark:from-amber-950/50 dark:to-amber-900/50 text-amber-600 dark:text-amber-400',
  orange: 'from-orange-50 to-orange-100 dark:from-orange-950/50 dark:to-orange-900/50 text-orange-600 dark:text-orange-400',
}

const valueClasses = {
  blue: 'text-blue-900 dark:text-blue-100',
  purple: 'text-purple-900 dark:text-purple-100',
  emerald: 'text-emerald-900 dark:text-emerald-100',
  rose: 'text-rose-900 dark:text-rose-100',
  amber: 'text-amber-900 dark:text-amber-100',
  orange: 'text-orange-900 dark:text-orange-100',
}

export function AnimatedMetricCard({
  label,
  value,
  suffix,
  description,
  icon,
  variant = 'blue',
  className,
  delay = 0,
}: AnimatedMetricCardProps) {
  const containerVariants = {
    ...fadeInUp,
    animate: {
      ...fadeInUp.animate,
      transition: {
        ...(fadeInUp.animate as any).transition,
        delay,
      },
    },
  }

  return (
    <motion.div
      className={cn(
        'relative overflow-hidden rounded-xl p-4 bg-gradient-to-br shadow-md transition-smooth hover:shadow-lg hover:-translate-y-0.5',
        variantClasses[variant],
        className
      )}
      initial="initial"
      animate="animate"
      variants={containerVariants}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Icon */}
      {icon && (
        <motion.div
          className="absolute top-3 right-3 opacity-20"
          variants={scaleIn}
          transition={{ delay: delay + 0.2 }}
        >
          {icon}
        </motion.div>
      )}

      {/* Label */}
      <motion.div
        className={cn('text-xs font-medium uppercase tracking-wide', variantClasses[variant].split(' ')[0])}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.1 }}
      >
        {label}
      </motion.div>

      {/* Value */}
      <motion.div
        className={cn('text-2xl font-bold mt-1 flex items-baseline gap-1', valueClasses[variant])}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.2, duration: 0.5 }}
      >
        <span>{value}</span>
        {suffix && <span className="text-lg font-normal opacity-70">{suffix}</span>}
      </motion.div>

      {/* Description */}
      {description && (
        <motion.div
          className={cn('text-xs mt-1 opacity-80', variantClasses[variant].split(' ')[0])}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.8 }}
          transition={{ delay: delay + 0.3 }}
        >
          {description}
        </motion.div>
      )}

      {/* Shimmer effect on hover */}
      <motion.div
        className="absolute inset-0 shimmer opacity-0 hover:opacity-100 transition-opacity pointer-events-none"
        initial={false}
      />
    </motion.div>
  )
}
