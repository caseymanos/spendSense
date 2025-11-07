'use client'

import React from 'react'
import type { Recommendation } from '../lib/types'
import { Card, CardContent } from './ui/card'
import { RecommendationChatDialog } from './RecommendationChatDialog'
import { CreditUtilizationMotion } from './charts/CreditUtilizationMotion'
import { DebtAvalancheChart } from './charts/DebtAvalancheChart'

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  // Render chart based on content type
  const renderChart = () => {
    if (!rec.content || !rec.content.type) return null

    switch (rec.content.type) {
      case 'credit_utilization':
        return <CreditUtilizationMotion data={rec.content.data} className="mt-4" />
      case 'debt_avalanche':
        return <DebtAvalancheChart debts={rec.content.data} className="mt-4" />
      default:
        return null
    }
  }

  return (
    <Card className="mt-3">
      <CardContent className="py-4">
        <div className="font-semibold">{rec.title}</div>
        <div className="mt-1 text-sm text-muted-foreground">{rec.rationale}</div>
        {renderChart()}
        <RecommendationChatDialog recommendation={rec} />
      </CardContent>
    </Card>
  )
}
