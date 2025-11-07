'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface LiquidGlassCardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'gradient' | 'vibrant'
  hover?: boolean
}

export function LiquidGlassCard({
  children,
  className,
  variant = 'default',
  hover = true,
}: LiquidGlassCardProps) {
  const baseStyles = cn(
    // Glass morphism base
    'relative backdrop-blur-xl',
    'border border-white/20 dark:border-white/10',
    'shadow-xl shadow-black/5',
    'rounded-2xl overflow-hidden',
    // Background with transparency
    'bg-white/70 dark:bg-gray-900/70',
  )

  const variantStyles = {
    default: '',
    gradient: cn(
      'bg-gradient-to-br from-white/80 via-white/70 to-white/60',
      'dark:from-gray-900/80 dark:via-gray-900/70 dark:to-gray-900/60',
    ),
    vibrant: cn(
      'bg-gradient-to-br from-blue-500/20 via-purple-500/10 to-pink-500/20',
      'dark:from-blue-500/30 dark:via-purple-500/20 dark:to-pink-500/30',
    ),
  }

  const hoverStyles = hover
    ? 'transition-all duration-300 hover:shadow-2xl hover:border-white/30 dark:hover:border-white/20'
    : ''

  return (
    <motion.div
      className={cn(baseStyles, variantStyles[variant], hoverStyles, className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Floating gradient orbs for liquid effect */}
      <div className="absolute inset-0 opacity-30 pointer-events-none overflow-hidden">
        <motion.div
          className="absolute -top-1/2 -left-1/2 w-full h-full rounded-full bg-gradient-to-r from-blue-400/30 to-purple-400/30 blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, 50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute -bottom-1/2 -right-1/2 w-full h-full rounded-full bg-gradient-to-l from-pink-400/30 to-violet-400/30 blur-3xl"
          animate={{
            x: [0, -80, 0],
            y: [0, -60, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10">{children}</div>

      {/* Shine effect on hover */}
      {hover && (
        <motion.div
          className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none"
          style={{
            background:
              'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%)',
            backgroundSize: '200% 200%',
          }}
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            repeatType: 'reverse',
          }}
        />
      )}
    </motion.div>
  )
}

interface GlassMetricCardProps {
  label: string
  value: string | number
  description?: string
  icon?: React.ReactNode
  className?: string
  color?: 'blue' | 'purple' | 'emerald' | 'rose' | 'amber'
}

export function GlassMetricCard({
  label,
  value,
  description,
  icon,
  className,
  color = 'blue',
}: GlassMetricCardProps) {
  const colorStyles = {
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
    emerald: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30',
    rose: 'from-rose-500/20 to-rose-600/10 border-rose-500/30',
    amber: 'from-amber-500/20 to-amber-600/10 border-amber-500/30',
  }

  return (
    <motion.div
      className={cn(
        'relative p-4 rounded-xl backdrop-blur-md',
        'bg-gradient-to-br',
        colorStyles[color],
        'border border-white/20 dark:border-white/10',
        'shadow-lg hover:shadow-xl transition-all duration-300',
        className
      )}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, y: -2 }}
      transition={{ duration: 0.3 }}
    >
      {/* Backdrop glow */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/5 to-transparent" />

      <div className="relative z-10 space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-wide text-gray-600 dark:text-gray-400 font-medium">
            {label}
          </p>
          {icon && <div className="text-gray-500 dark:text-gray-400">{icon}</div>}
        </div>
        <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
        {description && (
          <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>
        )}
      </div>
    </motion.div>
  )
}
