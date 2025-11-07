'use client'

import React from 'react'
import { Card, ProgressBar, CategoryBar } from '@tremor/react'

interface EmergencyFundProgressProps {
  currentMonths: number
  targetMonths?: number
  className?: string
}

export function EmergencyFundProgress({
  currentMonths,
  targetMonths = 6,
  className = ''
}: EmergencyFundProgressProps) {
  const progressPercent = Math.min((currentMonths / targetMonths) * 100, 100)
  const minimumMonths = 3

  const getStatus = (months: number) => {
    if (months >= targetMonths) return { label: 'Excellent', color: 'emerald' }
    if (months >= minimumMonths) return { label: 'Good', color: 'blue' }
    if (months >= 1) return { label: 'Building', color: 'amber' }
    return { label: 'Getting Started', color: 'rose' }
  }

  const status = getStatus(currentMonths)

  // Category bar data for milestones
  const categoryData = [
    { name: 'Saved', value: Math.min(currentMonths, targetMonths), color: status.color },
    { name: 'Goal', value: Math.max(0, targetMonths - currentMonths), color: 'gray' }
  ]

  return (
    <Card className={className}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-tremor-title font-semibold text-tremor-content-strong">
              Emergency Fund Progress
            </h3>
            <p className="text-tremor-default text-tremor-content">
              Months of expenses covered
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-tremor-content-strong">
              {currentMonths.toFixed(1)}
            </div>
            <div className={`text-tremor-default font-medium`} style={{ color: status.color === 'emerald' ? '#10b981' : status.color === 'blue' ? '#3b82f6' : status.color === 'amber' ? '#f59e0b' : '#ef4444' }}>
              {status.label}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-tremor-default">
            <span className="text-tremor-content">Progress to {targetMonths}-month goal</span>
            <span className="font-medium text-tremor-content-strong">{progressPercent.toFixed(0)}%</span>
          </div>
          <ProgressBar
            value={progressPercent}
            color={status.color as any}
            className="mt-2"
          />
        </div>

        {/* Category Bar - Visual Breakdown */}
        <div className="space-y-2">
          <p className="text-tremor-default text-tremor-content">Fund Status</p>
          <CategoryBar
            values={[
              (Math.min(currentMonths, targetMonths) / targetMonths) * 100,
              (Math.max(0, targetMonths - currentMonths) / targetMonths) * 100
            ]}
            colors={[status.color as any, 'gray']}
            className="mt-2"
          />
          <div className="flex justify-between text-tremor-label text-tremor-content">
            <span>0 months</span>
            <span className="text-amber-600 font-medium">3 months (minimum)</span>
            <span className="text-emerald-600 font-medium">{targetMonths} months (target)</span>
          </div>
        </div>

        {/* Milestones */}
        <div className="grid grid-cols-2 gap-4">
          <div className={`rounded-tremor-default border-2 p-3 text-center ${
            currentMonths >= minimumMonths ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300'
          }`}>
            <div className="text-2xl font-bold">
              {currentMonths >= minimumMonths ? '✓' : '○'}
            </div>
            <div className="text-tremor-label text-tremor-content mt-1">
              3 Month Minimum
            </div>
          </div>
          <div className={`rounded-tremor-default border-2 p-3 text-center ${
            currentMonths >= targetMonths ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300'
          }`}>
            <div className="text-2xl font-bold">
              {currentMonths >= targetMonths ? '✓' : '○'}
            </div>
            <div className="text-tremor-label text-tremor-content mt-1">
              {targetMonths} Month Goal
            </div>
          </div>
        </div>

        {/* Guidance */}
        <div className="rounded-tremor-default bg-tremor-background-subtle p-4">
          <p className="text-tremor-default text-tremor-content">
            🛡️ <span className="font-medium">Emergency Fund:</span> Build 3-6 months of expenses to protect against unexpected events like job loss, medical bills, or major repairs.
          </p>
        </div>
      </div>
    </Card>
  )
}
