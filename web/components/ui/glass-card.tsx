import * as React from 'react'
import { motion, HTMLMotionProps } from 'framer-motion'
import { cn } from '@/lib/utils'
import { fadeInUp } from '@/lib/animations'

export interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children?: React.ReactNode
  className?: string
  variant?: 'default' | 'strong' | 'light' | 'gradient-blue' | 'gradient-emerald' | 'gradient-amber'
  animated?: boolean
  hover?: boolean
  glow?: boolean
}

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = 'default', animated = true, hover = false, glow = false, children, ...props }, ref) => {
    const variantClasses = {
      default: 'glass',
      strong: 'glass-strong',
      light: 'glass-light',
      'gradient-blue': 'glass-gradient-blue',
      'gradient-emerald': 'glass-gradient-emerald',
      'gradient-amber': 'glass-gradient-amber',
    }

    const baseClasses = cn(
      'rounded-xl p-6 transition-smooth',
      variantClasses[variant],
      glow && 'shadow-glow',
      hover && 'hover:-translate-y-1 hover:shadow-xl cursor-pointer',
      className
    )

    if (!animated) {
      return (
        <div ref={ref} className={baseClasses} {...(props as React.HTMLAttributes<HTMLDivElement>)}>
          {children}
        </div>
      )
    }

    return (
      <motion.div
        ref={ref}
        className={baseClasses}
        initial="initial"
        animate="animate"
        exit="exit"
        variants={fadeInUp}
        {...props}
      >
        {children}
      </motion.div>
    )
  }
)

GlassCard.displayName = 'GlassCard'

export { GlassCard }
