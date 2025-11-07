'use client'

import React from 'react'
import { Card, BarList, BadgeDelta, Divider } from '@tremor/react'

interface SubscriptionItem {
  name: string
  cost: number
  isActive: boolean
}

interface SubscriptionAuditChartProps {
  subscriptions: SubscriptionItem[]
  monthlySavings: number
  className?: string
}

export function SubscriptionAuditChart({
  subscriptions,
  monthlySavings,
  className = ''
}: SubscriptionAuditChartProps) {
  const activeSubscriptions = subscriptions.filter(s => s.isActive)
  const inactiveSubscriptions = subscriptions.filter(s => !s.isActive)

  const totalCurrent = subscriptions.reduce((sum, s) => sum + s.cost, 0)
  const totalAfter = totalCurrent - monthlySavings

  const valueFormatter = (value: number) => `$${value.toFixed(2)}`

  // Prepare data for active subscriptions bar list
  const activeData = activeSubscriptions.map(sub => ({
    name: sub.name,
    value: sub.cost,
    color: 'blue'
  }))

  // Prepare data for inactive subscriptions bar list
  const inactiveData = inactiveSubscriptions.map(sub => ({
    name: sub.name,
    value: sub.cost,
    color: 'rose'
  }))

  return (
    <Card className={className}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-tremor-title font-semibold text-tremor-content-strong">
              Subscription Audit
            </h3>
            <p className="text-tremor-default text-tremor-content">
              Optimize your recurring expenses
            </p>
          </div>
          {monthlySavings > 0 && (
            <BadgeDelta deltaType="moderateDecrease" size="lg">
              Save ${monthlySavings}/mo
            </BadgeDelta>
          )}
        </div>

        {/* Before/After Comparison */}
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-tremor-default border border-rose-200 bg-rose-50 p-4">
            <div className="text-tremor-label text-tremor-content-subtle">Current Spend</div>
            <div className="text-2xl font-bold text-rose-600">${totalCurrent.toFixed(2)}</div>
            <div className="text-tremor-label text-tremor-content">/month</div>
          </div>
          <div className="rounded-tremor-default border border-emerald-200 bg-emerald-50 p-4">
            <div className="text-tremor-label text-tremor-content-subtle">After Optimization</div>
            <div className="text-2xl font-bold text-emerald-600">${totalAfter.toFixed(2)}</div>
            <div className="text-tremor-label text-tremor-content">/month</div>
          </div>
        </div>

        {/* Active Subscriptions */}
        {activeData.length > 0 && (
          <>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-tremor-default font-medium text-tremor-content-strong">
                  Active Subscriptions
                </p>
                <p className="text-tremor-default text-tremor-content">
                  {activeData.length} services
                </p>
              </div>
              <BarList
                data={activeData}
                valueFormatter={valueFormatter}
                className="mt-2"
                color="blue"
              />
            </div>
            <Divider />
          </>
        )}

        {/* Unused Subscriptions */}
        {inactiveData.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-tremor-default font-medium text-rose-600">
                Consider Canceling
              </p>
              <p className="text-tremor-default font-medium text-rose-600">
                Save ${monthlySavings}/mo
              </p>
            </div>
            <BarList
              data={inactiveData}
              valueFormatter={valueFormatter}
              className="mt-2"
              color="rose"
            />
          </div>
        )}

        {/* Annual Impact */}
        {monthlySavings > 0 && (
          <div className="rounded-tremor-default bg-emerald-50 border border-emerald-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-tremor-default font-medium text-emerald-900">
                  Potential Annual Savings
                </div>
                <div className="text-tremor-label text-emerald-700">
                  By canceling unused subscriptions
                </div>
              </div>
              <div className="text-3xl font-bold text-emerald-600">
                ${(monthlySavings * 12).toFixed(0)}
              </div>
            </div>
          </div>
        )}

        {/* Guidance */}
        <div className="rounded-tremor-default bg-tremor-background-subtle p-4">
          <p className="text-tremor-default text-tremor-content">
            💡 <span className="font-medium">Audit Tip:</span> Review subscriptions quarterly. Cancel unused services and negotiate better rates on the ones you keep. Small monthly savings compound to significant annual amounts.
          </p>
        </div>
      </div>
    </Card>
  )
}
