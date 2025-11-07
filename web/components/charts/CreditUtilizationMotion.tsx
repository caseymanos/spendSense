'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, Badge, BarChart } from '@tremor/react'
import { BorderTrail } from '@/components/ui/border-trail'
import { AnimatedNumber, SlidingNumber } from '@/components/ui/animated-number'
import { CircularProgressPie } from '@/components/ui/circular-progress-pie'
import { AnimatedMetricCard } from '@/components/ui/animated-metric-card'
import { CounterText } from '@/components/ui/counter-text'
import { GlassCard } from '@/components/ui/glass-card'
import { fadeInUp, staggerContainer, staggerContainerFast, scaleIn, gentleFloat } from '@/lib/animations'
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

interface CreditUtilizationMotionProps {
  utilization: number
  cardMask?: string
  data?: CreditUtilizationData
  className?: string
}

export function CreditUtilizationMotion(props: CreditUtilizationMotionProps) {
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
    <div className={cn('relative rounded-xl min-h-fit', className)}>
      {/* Large Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-100 via-pink-50 to-blue-100 dark:from-purple-950/30 dark:via-pink-950/20 dark:to-blue-950/30 rounded-xl" />

      {/* Content */}
      <Card className="relative bg-white/70 dark:bg-gray-900/70 backdrop-blur-sm border-0 shadow-xl !overflow-visible">
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
            </div>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Card ending in {data.cardMask || 'XXXX'}
            </p>
          </div>
        </motion.div>

        {/* Main Gauge and Metrics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Progress Circle with Border Trail + Animated Number */}
          <motion.div
            variants={fadeInUp}
            className="flex flex-col items-center justify-center p-8 relative"
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{
                duration: 1.2,
                ease: [0.34, 1.56, 0.64, 1],
                delay: 0.2
              }}
              className="overflow-visible min-w-[240px] min-h-[240px] flex items-center justify-center"
            >
              <CircularProgressPie
                value={data.utilization}
                size={200}
                strokeWidth={14}
                color={colorHex}
                showGradient={true}
                showShadow={true}
                animationDuration={2.5}
              >
                <div className="text-center">
                  <div className="text-5xl font-bold" style={{ color: colorHex }}>
                    <AnimatedNumber
                      value={data.utilization}
                      decimals={1}
                      duration={2.5}
                      suffix="%"
                      delay={0.6}
                      className="tabular-nums"
                    />
                  </div>
                  <motion.div
                    className="text-sm text-gray-500 mt-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2 }}
                  >
                    utilized
                  </motion.div>
                </div>
              </CircularProgressPie>
            </motion.div>
          </motion.div>

          {/* Right: Animated Metric Cards with In-View Stagger */}
          {hasEnhancedData && (
            <motion.div
              className="grid grid-cols-2 gap-4"
              variants={staggerContainerFast}
            >
              <AnimatedMetricCard
                label="Current Balance"
                value={`$${data.currentBalance?.toLocaleString()}`}
                variant="blue"
                delay={0.4}
              />
              <AnimatedMetricCard
                label="Credit Limit"
                value={`$${data.creditLimit?.toLocaleString()}`}
                variant="purple"
                delay={0.5}
              />
              <AnimatedMetricCard
                label="Available Credit"
                value={`$${data.availableCredit?.toLocaleString()}`}
                variant="emerald"
                delay={0.6}
              />
              <AnimatedMetricCard
                label="Monthly Interest"
                value={`$${data.monthlyInterest?.toFixed(2)}`}
                description={`${data.apr?.toFixed(2)}% APR`}
                variant="rose"
                delay={0.7}
              />
            </motion.div>
          )}
        </div>

        {/* Balance Comparison Chart */}
        {hasEnhancedData && data.amountOverTarget! > 0 && (
          <motion.div
            variants={fadeInUp}
            className="space-y-3"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Balance vs. Recommended Target
            </h4>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.9 }}
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
              transition={{ delay: 1.3 }}
            >
              Pay down <span className="font-bold text-rose-600">${data.amountOverTarget?.toLocaleString()}</span> to reach the recommended 30% utilization
            </motion.p>
          </motion.div>
        )}

        {/* Payment Scenarios */}
        {hasEnhancedData && data.paymentScenarios && data.paymentScenarios.length > 0 && (
          <GlassCard variant="gradient-blue" animated={true} className="p-5 space-y-4">
            <motion.div
              variants={fadeInUp}
              className="flex items-center justify-between"
            >
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                Path to 30% Utilization
              </h4>
              <Badge color="indigo">Scenarios</Badge>
            </motion.div>

            <motion.div
              className="grid grid-cols-2 lg:grid-cols-4 gap-3"
              variants={staggerContainerFast}
            >
              {data.paymentScenarios.map((scenario, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => setSelectedScenario(idx)}
                  className={cn(
                    'p-4 rounded-xl border-2 transition-all backdrop-blur-sm',
                    selectedScenario === idx
                      ? 'border-indigo-500 bg-white/90 dark:bg-gray-900/90 shadow-xl shadow-indigo-500/20'
                      : 'border-white/30 dark:border-gray-700/30 bg-white/50 dark:bg-gray-800/50 hover:border-indigo-300 dark:hover:border-indigo-600'
                  )}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 + 0.3 }}
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.98 }}
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

            {/* Selected Scenario Details with smooth animation */}
            {data.paymentScenarios[selectedScenario] && (
              <motion.div
                key={selectedScenario}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                className="glass-strong rounded-lg p-4 border border-indigo-200 dark:border-indigo-800"
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
          </GlassCard>
        )}

        {/* Utilization Zones Guide */}
        <motion.div
          variants={fadeInUp}
          className="space-y-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 p-4"
        >
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Utilization Impact on Credit Score
          </div>
          <motion.div
            className="space-y-2"
            variants={staggerContainerFast}
          >
            {[
              { range: 'Excellent (0-30%)', impact: 'Optimal', color: 'bg-emerald-500', textColor: 'text-emerald-700 dark:text-emerald-400', min: 0, max: 30 },
              { range: 'Good (30-50%)', impact: 'Minor impact', color: 'bg-yellow-500', textColor: 'text-yellow-700 dark:text-yellow-400', min: 30, max: 50 },
              { range: 'Fair (50-80%)', impact: 'Moderate impact', color: 'bg-orange-500', textColor: 'text-orange-700 dark:text-orange-400', min: 50, max: 80 },
              { range: 'High Risk (80-100%)', impact: 'Major impact', color: 'bg-red-500', textColor: 'text-red-700 dark:text-red-400', min: 80, max: 100 },
            ].map((zone, idx) => {
              const isCurrentLevel = data.utilization >= zone.min && data.utilization < zone.max
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 + 0.5 }}
                  className={cn(
                    'flex items-center justify-between text-sm p-2 rounded transition-colors',
                    isCurrentLevel
                      ? 'bg-gray-200 dark:bg-gray-700 border-2 border-gray-400 dark:border-gray-500'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700/50'
                  )}
                >
                  <div className="flex items-center gap-2">
                    <motion.div
                      className={cn('h-3 w-3 rounded-full', zone.color)}
                      whileHover={{ scale: 1.4 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                    />
                    <span className={cn('text-gray-600 dark:text-gray-400', isCurrentLevel && 'font-semibold text-gray-900 dark:text-gray-100')}>
                      {zone.range}
                    </span>
                  </div>
                  <span className={cn('font-medium', zone.textColor)}>{zone.impact}</span>
                </motion.div>
              )
            })}
          </motion.div>
        </motion.div>

        {/* Pro Tip */}
        <motion.div
          variants={fadeInUp}
          className="rounded-lg border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/30 p-4 shadow-glow"
        >
          <div className="flex">
            <motion.div
              className="flex-shrink-0"
              whileHover={{ rotate: [0, -10, 10, -10, 0] }}
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
    </Card>
    </div>
  )
}
