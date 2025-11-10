'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { ProgressCircle, Badge, BarChart } from '@tremor/react'
import { LiquidGlassCard, GlassMetricCard } from '@/components/ui/liquid-glass-card'
import { CounterText } from '@/components/ui/counter-text'
import { fadeInUp, staggerContainer, staggerContainerFast, scaleIn } from '@/lib/animations'
import { cn } from '@/lib/utils'

interface PaymentScenario {
  months: number
  monthlyPayment: number
  totalInterest: number
  totalPaid: number
}

interface CreditUtilizationData {
  utilization: number
  cardMask?: string
  currentBalance?: number
  creditLimit?: number
  availableCredit?: number
  apr?: number
  monthlyInterest?: number
  recommendedBalance?: number
  amountOverTarget?: number
  minimumPayment?: number
  paymentScenarios?: PaymentScenario[]
}

interface CreditUtilizationGlassProps {
  utilization: number
  cardMask?: string
  data?: CreditUtilizationData
  className?: string
}

export function CreditUtilizationGlass(props: CreditUtilizationGlassProps) {
  const { className = '' } = props

  const data: CreditUtilizationData = props.data || {
    utilization: props.utilization,
    cardMask: props.cardMask,
  }

  const [selectedScenario, setSelectedScenario] = useState(0)

  const getColor = (util: number): 'emerald' | 'yellow' | 'orange' | 'red' => {
    if (util < 30) return 'emerald'
    if (util < 50) return 'yellow'
    if (util < 80) return 'orange'
    return 'red'
  }

  const getLabel = (util: number): string => {
    if (util < 30) return 'Excellent'
    if (util < 50) return 'Good'
    if (util < 80) return 'Fair'
    return 'High Risk'
  }

  const getColorHex = (util: number): string => {
    if (util < 30) return '#10b981'
    if (util < 50) return '#eab308'
    if (util < 80) return '#f97316'
    return '#ef4444'
  }

  const color = getColor(data.utilization)
  const label = getLabel(data.utilization)
  const colorHex = getColorHex(data.utilization)

  const hasEnhancedData = !!data.currentBalance

  const balanceComparison = hasEnhancedData ? [
    {
      category: 'Current',
      'Balance': data.currentBalance,
      'Recommended (30%)': data.recommendedBalance,
    }
  ] : []

  return (
    <LiquidGlassCard variant="vibrant" className={cn('p-6', className)}>
      <motion.div
        className="space-y-6"
        initial="initial"
        animate="animate"
        variants={staggerContainer}
      >
        {/* Header */}
        <motion.div variants={fadeInUp} className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Credit Utilization
              </h3>
              <motion.div variants={scaleIn}>
                <Badge color={color} size="sm">
                  {label}
                </Badge>
              </motion.div>
              <div className="text-xs px-2 py-1 rounded-full bg-gradient-to-r from-pink-500/30 to-violet-500/30 text-pink-700 dark:text-pink-300 border border-pink-500/40 backdrop-blur-sm">
                Glass Mode
              </div>
            </div>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Card ending in {data.cardMask || 'XXXX'}
            </p>
          </div>
        </motion.div>

        {/* Main Gauge and Metrics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Progress Circle in Glass Container */}
          <motion.div
            variants={fadeInUp}
            className="flex flex-col items-center justify-center py-4 relative"
          >
            <div className="relative p-8 rounded-3xl backdrop-blur-2xl bg-gradient-to-br from-white/40 via-white/30 to-white/20 dark:from-gray-800/40 dark:via-gray-800/30 dark:to-gray-800/20 border border-white/30 dark:border-white/10 shadow-2xl">
              {/* Floating gradient orbs behind progress */}
              <motion.div
                className="absolute top-0 left-0 w-32 h-32 rounded-full blur-3xl opacity-50"
                style={{ background: colorHex }}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.6, 0.3],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />

              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{
                  duration: 1,
                  ease: [0.34, 1.56, 0.64, 1],
                  delay: 0.2
                }}
              >
                <ProgressCircle value={data.utilization} size="xl" color={color}>
                  <div className="text-center">
                    <motion.div
                      className="text-4xl font-bold backdrop-blur-sm"
                      style={{ color: colorHex }}
                      initial={{ opacity: 0, scale: 0.5 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.8, duration: 0.5 }}
                    >
                      <CounterText value={data.utilization} decimals={1} duration={1.5} suffix="%" />
                    </motion.div>
                    <motion.div
                      className="text-sm text-gray-500 mt-1"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 1 }}
                    >
                      utilized
                    </motion.div>
                  </div>
                </ProgressCircle>
              </motion.div>

              {/* Pulsing indicator */}
              {data.utilization > 30 && (
                <motion.div
                  className="absolute -right-2 -top-2 text-xl"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 1, type: 'spring' }}
                >
                  <motion.span
                    animate={{
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                    }}
                  >
                    ⚠️
                  </motion.span>
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Right: Glass Morphism Metric Cards */}
          {hasEnhancedData && (
            <motion.div
              className="grid grid-cols-2 gap-4"
              variants={staggerContainerFast}
            >
              <GlassMetricCard
                label="Current Balance"
                value={`$${(data.currentBalance ?? 0).toLocaleString()}`}
                color="blue"
              />
              <GlassMetricCard
                label="Credit Limit"
                value={`$${(data.creditLimit ?? 0).toLocaleString()}`}
                color="purple"
              />
              <GlassMetricCard
                label="Available Credit"
                value={`$${(data.availableCredit ?? 0).toLocaleString()}`}
                color="emerald"
              />
              <GlassMetricCard
                label="Monthly Interest"
                value={`$${(data.monthlyInterest ?? 0).toFixed(2)}`}
                description={`${(data.apr ?? 0).toFixed(2)}% APR`}
                color="rose"
              />
            </motion.div>
          )}
        </div>

        {/* Balance Comparison Chart in Glass Container */}
        {hasEnhancedData && data.amountOverTarget! > 0 && (
          <motion.div
            variants={fadeInUp}
            className="space-y-3 p-5 rounded-2xl backdrop-blur-xl bg-white/50 dark:bg-gray-800/50 border border-white/30 dark:border-white/10"
          >
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Balance vs. Recommended Target
            </h4>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.7 }}
            >
              <BarChart
                data={balanceComparison}
                index="category"
                categories={['Balance', 'Recommended (30%)']}
                colors={['rose', 'emerald']}
                valueFormatter={(value) => `$${value.toLocaleString()}`}
                yAxisWidth={60}
                className="h-32"
                showAnimation={true}
                showLegend={false}
              />
            </motion.div>
            <motion.p
              className="text-sm text-gray-600 dark:text-gray-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
            >
              Pay down <span className="font-bold text-rose-600">${data.amountOverTarget?.toLocaleString()}</span> to reach the recommended 30% utilization
            </motion.p>
          </motion.div>
        )}

        {/* Payment Scenarios in Glass Card */}
        {hasEnhancedData && data.paymentScenarios && data.paymentScenarios.length > 0 && (
          <motion.div
            variants={fadeInUp}
            className="p-5 space-y-4 rounded-2xl backdrop-blur-xl bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10 border border-indigo-500/20"
          >
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                Path to 30% Utilization
              </h4>
              <Badge color="indigo">Scenarios</Badge>
            </div>

            <motion.div
              className="grid grid-cols-2 lg:grid-cols-4 gap-3"
              variants={staggerContainerFast}
            >
              {data.paymentScenarios.map((scenario, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => setSelectedScenario(idx)}
                  className={cn(
                    'p-4 rounded-xl border-2 transition-all backdrop-blur-lg',
                    selectedScenario === idx
                      ? 'border-indigo-400 bg-white/90 dark:bg-gray-900/90 shadow-2xl shadow-indigo-500/30'
                      : 'border-white/40 dark:border-gray-700/40 bg-white/60 dark:bg-gray-800/60 hover:border-indigo-300 dark:hover:border-indigo-500'
                  )}
                  variants={scaleIn}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                    {scenario.months} Months
                  </div>
                  <div className="text-xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                    ${scenario.monthlyPayment.toLocaleString()}
                    <span className="text-sm font-normal text-gray-500 dark:text-gray-400">/mo</span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    ${scenario.totalInterest.toFixed(0)} interest
                  </div>
                </motion.button>
              ))}
            </motion.div>

            {/* Selected Scenario Details */}
            {data.paymentScenarios[selectedScenario] && (
              <motion.div
                key={selectedScenario}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="rounded-lg p-4 border border-indigo-300/50 dark:border-indigo-700/50 backdrop-blur-xl bg-white/70 dark:bg-gray-900/70"
              >
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase">Timeline</div>
                    <div className="text-lg font-bold text-gray-900 dark:text-gray-100 mt-1">
                      <CounterText
                        value={data.paymentScenarios[selectedScenario].months}
                        duration={0.5}
                        suffix=" months"
                      />
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase">Total Interest</div>
                    <div className="text-lg font-bold text-rose-600 dark:text-rose-400 mt-1">
                      $<CounterText
                        value={data.paymentScenarios[selectedScenario].totalInterest}
                        duration={0.5}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase">Total Paid</div>
                    <div className="text-lg font-bold text-gray-900 dark:text-gray-100 mt-1">
                      $<CounterText
                        value={data.paymentScenarios[selectedScenario].totalPaid}
                        duration={0.5}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Utilization Zones Guide */}
        <motion.div
          variants={fadeInUp}
          className="space-y-3 rounded-xl backdrop-blur-lg bg-gray-50/80 dark:bg-gray-800/80 p-4 border border-white/20 dark:border-white/10"
        >
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Utilization Impact on Credit Score
          </div>
          <motion.div
            className="space-y-2"
            variants={staggerContainerFast}
          >
            {[
              { range: 'Excellent (0-30%)', impact: 'Optimal', color: 'bg-emerald-500', textColor: 'text-emerald-700 dark:text-emerald-400' },
              { range: 'Good (30-50%)', impact: 'Minor impact', color: 'bg-yellow-500', textColor: 'text-yellow-700 dark:text-yellow-400' },
              { range: 'Fair (50-80%)', impact: 'Moderate impact', color: 'bg-orange-500', textColor: 'text-orange-700 dark:text-orange-400' },
              { range: 'High Risk (80-100%)', impact: 'Major impact', color: 'bg-red-500', textColor: 'text-red-700 dark:text-red-400' },
            ].map((zone, idx) => (
              <motion.div
                key={idx}
                variants={scaleIn}
                className="flex items-center justify-between text-sm hover:bg-white/60 dark:hover:bg-gray-700/60 p-2 rounded transition-colors backdrop-blur-sm"
              >
                <div className="flex items-center gap-2">
                  <motion.div
                    className={cn('h-3 w-3 rounded-full shadow-lg', zone.color)}
                    whileHover={{ scale: 1.3, boxShadow: '0 0 12px currentColor' }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  />
                  <span className="text-gray-600 dark:text-gray-400">{zone.range}</span>
                </div>
                <span className={cn('font-medium', zone.textColor)}>{zone.impact}</span>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Pro Tip */}
        <motion.div
          variants={fadeInUp}
          className="rounded-xl border-l-4 border-blue-400 backdrop-blur-lg bg-blue-50/80 dark:bg-blue-950/50 p-4 shadow-lg"
        >
          <div className="flex">
            <motion.div
              className="flex-shrink-0"
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              <svg className="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </motion.div>
            <div className="ml-3">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <span className="font-semibold">Pro tip:</span> Keeping utilization below 30% can improve your credit score by 100+ points and demonstrates strong credit management to lenders.
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </LiquidGlassCard>
  )
}
