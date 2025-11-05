'use client'

import React from 'react'
import { Card, CardContent } from './ui/card'

export function MetricCard({ label, value, help, color }: { label: string; value: string; help?: string; color?: string }) {
  return (
    <Card>
      <CardContent className="space-y-1 py-4">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="text-2xl font-bold" style={{ color: color || 'hsl(var(--primary))' }}>{value}</div>
        {help ? <div className="text-xs text-muted-foreground">{help}</div> : null}
      </CardContent>
    </Card>
  )
}
