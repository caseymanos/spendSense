'use client'

import React from 'react'
import { Card, CardContent } from './ui/card'

export function PersonaBadge({ icon = '🌱', title, description, color }: { icon?: string; title: string; description?: string; color?: string }) {
  return (
    <Card className="border-l-4" style={{ borderLeftColor: color || '#A8DADC' }}>
      <CardContent className="py-4">
        <div className="text-xl font-bold">{icon} {title}</div>
        {description ? <div className="mt-1 text-muted-foreground">{description}</div> : null}
      </CardContent>
    </Card>
  )
}
