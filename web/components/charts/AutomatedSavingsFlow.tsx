'use client'

import React from 'react'
import { Card, CategoryBar } from '@tremor/react'
import { ResponsiveSankey } from '@nivo/sankey'

interface AutomatedSavingsFlowProps {
  savingsPercent: number
  className?: string
}

export function AutomatedSavingsFlow({
  savingsPercent,
  className = ''
}: AutomatedSavingsFlowProps) {
  const checkingPercent = 100 - savingsPercent

  // Sankey diagram data
  const sankeyData = {
    nodes: [
      { id: 'Paycheck', color: '#3b82f6' },
      { id: `Savings Account (${savingsPercent}%)`, color: '#10b981' },
      { id: `Checking Account (${checkingPercent}%)`, color: '#6b7280' }
    ],
    links: [
      {
        source: 'Paycheck',
        target: `Savings Account (${savingsPercent}%)`,
        value: savingsPercent
      },
      {
        source: 'Paycheck',
        target: `Checking Account (${checkingPercent}%)`,
        value: checkingPercent
      }
    ]
  }

  return (
    <Card className={className}>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h3 className="text-tremor-title font-semibold text-tremor-content-strong">
            Automated Savings Flow
          </h3>
          <p className="text-tremor-default text-tremor-content">
            Pay yourself first - automatically
          </p>
        </div>

        {/* Sankey Diagram */}
        <div className="h-64">
          <ResponsiveSankey
            data={sankeyData}
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            align="justify"
            colors={['#3b82f6', '#10b981', '#6b7280']}
            nodeOpacity={1}
            nodeThickness={18}
            nodeSpacing={24}
            nodeBorderWidth={0}
            linkOpacity={0.3}
            linkHoverOpacity={0.6}
            linkContract={3}
            enableLinkGradient={true}
            labelPosition="inside"
            labelOrientation="horizontal"
            labelPadding={16}
            labelTextColor="white"
            animate={true}
            motionConfig="gentle"
          />
        </div>

        {/* Category Bar Breakdown */}
        <div className="space-y-2">
          <p className="text-tremor-default text-tremor-content">Split Breakdown</p>
          <CategoryBar
            values={[savingsPercent, checkingPercent]}
            colors={['emerald', 'gray']}
            markerValue={savingsPercent}
            tooltip={`${savingsPercent}% to savings`}
            className="mt-2"
          />
          <div className="flex justify-between text-tremor-label">
            <span className="text-emerald-600 font-medium">
              {savingsPercent}% to Savings
            </span>
            <span className="text-gray-600 font-medium">
              {checkingPercent}% to Checking
            </span>
          </div>
        </div>

        {/* Recommendations by Tier */}
        <div className="space-y-3">
          <p className="text-tremor-default font-medium text-tremor-content-strong">
            Savings Rate Goals
          </p>
          <div className="grid grid-cols-3 gap-3">
            <div className={`rounded-tremor-default border-2 p-3 text-center ${
              savingsPercent >= 10 ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300'
            }`}>
              <div className="text-2xl font-bold">
                {savingsPercent >= 10 ? '✓' : '10%'}
              </div>
              <div className="text-tremor-label text-tremor-content mt-1">
                Minimum
              </div>
            </div>
            <div className={`rounded-tremor-default border-2 p-3 text-center ${
              savingsPercent >= 20 ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}>
              <div className="text-2xl font-bold">
                {savingsPercent >= 20 ? '✓' : '20%'}
              </div>
              <div className="text-tremor-label text-tremor-content mt-1">
                Good
              </div>
            </div>
            <div className={`rounded-tremor-default border-2 p-3 text-center ${
              savingsPercent >= 30 ? 'border-purple-500 bg-purple-50' : 'border-gray-300'
            }`}>
              <div className="text-2xl font-bold">
                {savingsPercent >= 30 ? '✓' : '30%'}
              </div>
              <div className="text-tremor-label text-tremor-content mt-1">
                Excellent
              </div>
            </div>
          </div>
        </div>

        {/* Current Status */}
        {savingsPercent < 10 && (
          <div className="rounded-tremor-default bg-amber-50 border border-amber-200 p-4">
            <p className="text-tremor-default text-amber-900">
              ⚠️ <span className="font-medium">Getting Started:</span> Try to increase your savings rate to at least 10%. Even small increases compound significantly over time.
            </p>
          </div>
        )}

        {savingsPercent >= 10 && savingsPercent < 20 && (
          <div className="rounded-tremor-default bg-blue-50 border border-blue-200 p-4">
            <p className="text-tremor-default text-blue-900">
              💙 <span className="font-medium">Good Progress:</span> You're saving {savingsPercent}%! Consider gradually increasing to 20% for stronger long-term growth.
            </p>
          </div>
        )}

        {savingsPercent >= 20 && (
          <div className="rounded-tremor-default bg-emerald-50 border border-emerald-200 p-4">
            <p className="text-tremor-default text-emerald-900">
              🌟 <span className="font-medium">Excellent Work:</span> Saving {savingsPercent}% puts you well ahead. Keep this automation running to build long-term wealth.
            </p>
          </div>
        )}

        {/* Guidance */}
        <div className="rounded-tremor-default bg-tremor-background-subtle p-4">
          <p className="text-tremor-default text-tremor-content">
            ✨ <span className="font-medium">Automation Tip:</span> Set up automatic transfers on payday. This "pay yourself first" strategy ensures consistent saving without requiring willpower each month.
          </p>
        </div>
      </div>
    </Card>
  )
}
