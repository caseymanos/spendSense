'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, BadgeDelta, Badge } from '@tremor/react'
import { AnimatedMetricCard } from '@/components/ui/animated-metric-card'
import { CounterText } from '@/components/ui/counter-text'
import { GlassCard } from '@/components/ui/glass-card'
import {
  fadeInUp,
  staggerContainer,
  staggerContainerFast,
  scaleIn,
  slideInLeft,
  rotateBadge,
  gentleFloat
} from '@/lib/animations'
import { cn } from '@/lib/utils'

interface DebtData {
  name: string
  balance: number
  interestRate: number
  priority: number
  minimumPayment?: number
  monthlyInterest?: number
}

interface PayoffScenario {
  extraPayment: number
  totalMonthlyPayment: number
  monthsToPayoff: number
  yearsToPayoff: number
  totalInterestPaid: number
  totalPaid: number
}

interface DebtSummary {
  totalDebt: number
  totalMinimumPayment: number
  totalMonthlyInterest: number
  averageAPR: number
  debtCount: number
}

interface DebtAvalancheData {
  debts?: DebtData[]
  summary?: DebtSummary
  payoffScenarios?: PayoffScenario[]
  interestSavings?: number
  timeSavingsMonths?: number
  timeSavingsYears?: number
}

interface DebtAvalancheChartProps {
  debts: DebtData[]
  data?: DebtAvalancheData
  className?: string
}

export function DebtAvalancheChart({ debts: legacyDebts, data, className = '' }: DebtAvalancheChartProps) {
  const [selectedScenario, setSelectedScenario] = useState(2) // Default to middle scenario

  const debts = data?.debts || legacyDebts || []
  const hasEnhancedData = !!data?.summary

  const sortedDebts = [...debts].sort((a, b) => b.interestRate - a.interestRate)

  const chartData = sortedDebts.map((debt, index) => ({
    name: debt.name,
    Balance: debt.balance,
    'Interest Rate': debt.interestRate,
    priority: index + 1
  }))

  const valueFormatter = (value: number) => `$${value.toLocaleString()}`
  const rateFormatter = (value: number) => `${value.toFixed(2)}%`

  if (debts.length === 0) {
    return (
      <Card className={className}>
        <motion.div
          className="space-y-4"
          initial="initial"
          animate="animate"
          variants={staggerContainer}
        >
          <motion.div variants={fadeInUp}>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Debt Avalanche Strategy
            </h3>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Highest interest first to save on total interest
            </p>
          </motion.div>
          <motion.div
            variants={fadeInUp}
            className="flex flex-col items-center justify-center py-12"
          >
            <motion.div
              className="rounded-full bg-green-100 dark:bg-green-900/30 p-4 mb-4"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
            >
              <svg className="h-12 w-12 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </motion.div>
            <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100">No Debt to Prioritize</h4>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 text-center max-w-md">
              You don't have multiple debts to prioritize at the moment. The debt avalanche method will be useful if you have multiple debts with different interest rates.
            </p>
          </motion.div>
        </motion.div>
      </Card>
    )
  }

  const getDebtFreeDate = (months: number) => {
    const date = new Date()
    date.setMonth(date.getMonth() + months)
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }

  return (
    <Card className={className}>
      <motion.div
        className="space-y-6"
        initial="initial"
        animate="animate"
        variants={staggerContainer}
      >
        {/* Header */}
        <motion.div variants={fadeInUp} className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Debt Avalanche Strategy
            </h3>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Highest interest first to save on total interest
            </p>
          </div>
          <motion.div variants={scaleIn}>
            <BadgeDelta deltaType="moderateDecrease" size="lg">
              Optimized
            </BadgeDelta>
          </motion.div>
        </motion.div>

        {/* Summary Metrics with AnimatedMetricCard */}
        {hasEnhancedData && data.summary && (
          <motion.div
            className="grid grid-cols-2 lg:grid-cols-4 gap-4"
            variants={staggerContainerFast}
          >
            <AnimatedMetricCard
              label="Total Debt"
              value={`$${data.summary.totalDebt.toLocaleString()}`}
              description={`${data.summary.debtCount} ${data.summary.debtCount === 1 ? 'account' : 'accounts'}`}
              variant="rose"
              delay={0.2}
            />
            <AnimatedMetricCard
              label="Monthly Interest"
              value={`$${data.summary.totalMonthlyInterest.toFixed(2)}`}
              description={`${data.summary.averageAPR.toFixed(2)}% Avg APR`}
              variant="orange"
              delay={0.3}
            />
            <AnimatedMetricCard
              label="Minimum Payment"
              value={`$${data.summary.totalMinimumPayment.toFixed(2)}`}
              description="per month"
              variant="amber"
              delay={0.4}
            />
            {data.interestSavings && data.interestSavings > 0 && (
              <AnimatedMetricCard
                label="Potential Savings"
                value={`$${data.interestSavings.toLocaleString()}`}
                description="in interest"
                variant="emerald"
                delay={0.5}
              />
            )}
          </motion.div>
        )}

        {/* Payoff Scenarios with GlassCard */}
        {hasEnhancedData && data.payoffScenarios && data.payoffScenarios.length > 0 && (
          <GlassCard variant="gradient-emerald" animated={true} className="p-5 space-y-4">
            <motion.div
              variants={fadeInUp}
              className="flex items-center justify-between"
            >
              <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                Payoff Timeline Scenarios
              </h4>
              <Badge color="blue">Interactive</Badge>
            </motion.div>

            <motion.div
              className="grid grid-cols-2 lg:grid-cols-5 gap-3"
              variants={staggerContainerFast}
            >
              {data.payoffScenarios.map((scenario, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => setSelectedScenario(idx)}
                  className={cn(
                    'p-4 rounded-xl border-2 transition-all backdrop-blur-sm',
                    selectedScenario === idx
                      ? 'border-blue-500 bg-white/90 dark:bg-gray-900/90 shadow-xl shadow-blue-500/20'
                      : 'border-white/30 dark:border-gray-700/30 bg-white/50 dark:bg-gray-800/50 hover:border-blue-300 dark:hover:border-blue-600'
                  )}
                  variants={scaleIn}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                    {scenario.extraPayment === 0 ? 'Minimum Only' : `+$${scenario.extraPayment}/mo`}
                  </div>
                  <div className="text-xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                    {scenario.yearsToPayoff} <span className="text-sm font-normal">yrs</span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    ${scenario.totalInterestPaid.toLocaleString()} interest
                  </div>
                </motion.button>
              ))}
            </motion.div>

            {/* Selected Scenario Detailed View */}
            {data.payoffScenarios[selectedScenario] && (
              <motion.div
                key={selectedScenario}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="glass-strong rounded-lg p-5 border-2 border-blue-200 dark:border-blue-800"
              >
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">Monthly Payment</div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-1">
                      $<CounterText
                        value={data.payoffScenarios[selectedScenario].totalMonthlyPayment}
                        duration={0.5}
                      />
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {data.payoffScenarios[selectedScenario].extraPayment > 0 && (
                        <span className="text-blue-600 dark:text-blue-400 font-medium">
                          +${data.payoffScenarios[selectedScenario].extraPayment} extra
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">Time to Payoff</div>
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
                      <CounterText
                        value={data.payoffScenarios[selectedScenario].monthsToPayoff}
                        duration={0.5}
                        suffix=" mo"
                      />
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {data.payoffScenarios[selectedScenario].yearsToPayoff} years
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">Total Interest</div>
                    <div className="text-2xl font-bold text-orange-600 dark:text-orange-400 mt-1">
                      $<CounterText
                        value={data.payoffScenarios[selectedScenario].totalInterestPaid}
                        duration={0.5}
                      />
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">over lifetime</div>
                  </div>

                  <div className="text-center">
                    <div className="text-xs text-gray-600 dark:text-gray-400 uppercase tracking-wide">Debt-Free Date</div>
                    <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-1">
                      {getDebtFreeDate(data.payoffScenarios[selectedScenario].monthsToPayoff)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">projected</div>
                  </div>
                </div>

                {/* Savings vs Minimum Only */}
                {selectedScenario > 0 && data.payoffScenarios[0] && (
                  <motion.div
                    className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                  >
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">vs. Minimum Payments:</span>
                      <div className="flex gap-4">
                        <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                          Save ${(data.payoffScenarios[0].totalInterestPaid - data.payoffScenarios[selectedScenario].totalInterestPaid).toLocaleString()} interest
                        </span>
                        <span className="text-blue-600 dark:text-blue-400 font-bold">
                          {((data.payoffScenarios[0].monthsToPayoff - data.payoffScenarios[selectedScenario].monthsToPayoff) / 12).toFixed(1)} years faster
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </GlassCard>
        )}

        {/* Priority List with Sequential Animations */}
        <motion.div variants={fadeInUp} className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Payment Priority Order (Avalanche Method)
            </p>
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, type: 'spring' }}
            >
              <Badge color="rose" size="sm">
                {sortedDebts.length} {sortedDebts.length === 1 ? 'Debt' : 'Debts'}
              </Badge>
            </motion.div>
          </div>
          <motion.div
            className="space-y-3"
            variants={staggerContainerFast}
          >
            {sortedDebts.map((debt, index) => (
              <motion.div
                key={debt.name}
                variants={slideInLeft}
                className={cn(
                  'relative overflow-hidden rounded-2xl backdrop-blur-xl border-2 p-5 transition-all group',
                  index === 0
                    ? 'border-rose-200 dark:border-rose-800 bg-gradient-to-br from-rose-50/80 via-white/60 to-pink-50/80 dark:from-rose-950/30 dark:via-gray-900/60 dark:to-pink-950/30'
                    : 'border-gray-200/60 dark:border-gray-700/60 bg-gradient-to-br from-white/70 via-gray-50/50 to-white/70 dark:from-gray-800/70 dark:via-gray-900/50 dark:to-gray-800/70',
                  'hover:shadow-2xl hover:border-rose-300 dark:hover:border-rose-600'
                )}
                whileHover={{ scale: 1.02, y: -4 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                {/* Gradient Background Orb */}
                <motion.div
                  className="absolute -right-8 -top-8 w-32 h-32 rounded-full blur-3xl opacity-20"
                  style={{
                    background: index === 0
                      ? 'linear-gradient(135deg, #f43f5e, #ec4899)'
                      : 'linear-gradient(135deg, #3b82f6, #8b5cf6)'
                  }}
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.2, 0.3, 0.2],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />

                <div className="relative flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <motion.div
                      className={cn(
                        'relative flex h-12 w-12 items-center justify-center rounded-2xl text-white font-bold text-xl shadow-2xl',
                        index === 0 ? 'bg-gradient-to-br from-rose-500 to-pink-600 shadow-rose-500/50' :
                        index === 1 ? 'bg-gradient-to-br from-amber-500 to-orange-600 shadow-amber-500/50' :
                        'bg-gradient-to-br from-blue-500 to-indigo-600 shadow-blue-500/50'
                      )}
                      whileHover={{
                        scale: 1.2,
                        rotate: [0, -10, 10, -10, 0],
                        boxShadow: index === 0
                          ? '0 20px 60px rgba(244, 63, 94, 0.6)'
                          : '0 20px 60px rgba(59, 130, 246, 0.6)'
                      }}
                      transition={{ type: 'spring', stiffness: 400, damping: 15 }}
                    >
                      <span className="relative z-10">{index + 1}</span>
                      <motion.div
                        className="absolute inset-0 rounded-2xl bg-white/20"
                        initial={{ scale: 0, opacity: 0 }}
                        whileHover={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      />
                    </motion.div>
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-gray-100 text-lg">
                        {debt.name}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-3 mt-1">
                        <span className="font-medium">{valueFormatter(debt.balance)} @ {rateFormatter(debt.interestRate)}</span>
                        {debt.monthlyInterest && (
                          <motion.span
                            className="px-2.5 py-1 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 font-semibold text-xs border border-orange-200 dark:border-orange-800"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 }}
                          >
                            ${debt.monthlyInterest.toFixed(2)}/mo interest
                          </motion.span>
                        )}
                      </div>
                    </div>
                  </div>
                  {index === 0 && (
                    <motion.div
                      className="flex flex-col items-end gap-1"
                      initial={{ opacity: 0, scale: 0, rotate: -180 }}
                      animate={{ opacity: 1, scale: 1, rotate: 0 }}
                      transition={{
                        delay: 0.5,
                        type: 'spring',
                        stiffness: 260,
                        damping: 20
                      }}
                    >
                      <motion.div
                        className="relative px-4 py-2 rounded-xl bg-gradient-to-r from-rose-500 to-pink-600 shadow-xl shadow-rose-500/50 border border-rose-400"
                        whileHover={{
                          scale: 1.1,
                          boxShadow: '0 20px 40px rgba(244, 63, 94, 0.6)',
                        }}
                        animate={{
                          boxShadow: [
                            '0 10px 30px rgba(244, 63, 94, 0.5)',
                            '0 15px 40px rgba(244, 63, 94, 0.7)',
                            '0 10px 30px rgba(244, 63, 94, 0.5)',
                          ]
                        }}
                        transition={{
                          boxShadow: {
                            duration: 2,
                            repeat: Infinity,
                            ease: 'easeInOut'
                          }
                        }}
                      >
                        <motion.span
                          className="text-sm font-bold text-white uppercase tracking-wider drop-shadow-lg"
                          animate={{
                            textShadow: [
                              '0 0 10px rgba(255,255,255,0.5)',
                              '0 0 20px rgba(255,255,255,0.8)',
                              '0 0 10px rgba(255,255,255,0.5)',
                            ]
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                          }}
                        >
                          PAY FIRST
                        </motion.span>
                        <motion.div
                          className="absolute -inset-1 bg-gradient-to-r from-rose-400 to-pink-500 rounded-xl opacity-30 blur-md"
                          animate={{
                            scale: [1, 1.1, 1],
                            opacity: [0.3, 0.5, 0.3],
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                          }}
                        />
                      </motion.div>
                      <span className="text-xs text-gray-600 dark:text-gray-400 font-medium">Highest APR</span>
                    </motion.div>
                  )}
                </div>

                {/* Hover Shimmer Effect */}
                <motion.div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                  }}
                  initial={{ x: '-100%' }}
                  whileHover={{ x: '100%' }}
                  transition={{ duration: 0.8, ease: 'easeInOut' }}
                />
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Strategy Explanation */}
        <motion.div
          variants={fadeInUp}
          className="rounded-lg bg-gray-50 dark:bg-gray-800/50 p-4"
        >
          <p className="text-sm text-gray-700 dark:text-gray-300">
            💡 <span className="font-medium">Avalanche Method:</span> Focus extra payments on {sortedDebts[0]?.name} (highest interest: {rateFormatter(sortedDebts[0]?.interestRate)}) while making minimum payments on others. This mathematically saves the most on total interest over time compared to other strategies.
          </p>
        </motion.div>

        {/* Interest Savings Highlight */}
        {hasEnhancedData && data.interestSavings && data.interestSavings > 0 && (
          <motion.div
            variants={fadeInUp}
            className="rounded-lg border-l-4 border-emerald-500 bg-emerald-50 dark:bg-emerald-950/30 p-4 shadow-glow-emerald"
          >
            <div className="flex">
              <motion.div
                className="flex-shrink-0"
                whileHover={{ scale: 1.2, rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <svg className="h-6 w-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </motion.div>
              <div className="ml-3">
                <p className="text-sm text-emerald-800 dark:text-emerald-200">
                  <span className="font-semibold">💰 Potential Savings:</span> By paying an extra ${data.payoffScenarios?.[data.payoffScenarios.length - 1]?.extraPayment}/month, you could save <span className="font-bold text-emerald-900 dark:text-emerald-100">${data.interestSavings.toLocaleString()}</span> in interest charges and become debt-free <span className="font-bold text-emerald-900 dark:text-emerald-100">{data.timeSavingsYears?.toFixed(1)} years faster</span>!
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </Card>
  )
}
