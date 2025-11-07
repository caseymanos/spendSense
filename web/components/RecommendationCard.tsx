'use client'

import React from 'react'
import type { Recommendation } from '../lib/types'
import { Card, CardContent } from './ui/card'
import { RecommendationChatDialog } from './RecommendationChatDialog'

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <Card className="mt-3">
      <CardContent className="py-4">
        <div className="font-semibold">{rec.title}</div>
        <div className="mt-1 text-sm text-muted-foreground">{rec.rationale}</div>
        <RecommendationChatDialog recommendation={rec} />
      </CardContent>
    </Card>
  )
}
