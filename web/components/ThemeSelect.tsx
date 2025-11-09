'use client'

import * as React from 'react'
import { useTheme } from 'next-themes'

const AVAILABLE_THEMES = ['light', 'dark']

export function ThemeSelect() {
  const { theme, setTheme } = useTheme()
  return (
    <div className="ml-auto flex items-center gap-2">
      <label className="text-sm text-muted-foreground">Theme</label>
      <select
        className="h-9 rounded-md border bg-background px-2 text-sm"
        value={theme as string}
        onChange={(e) => setTheme(e.target.value)}
      >
        {AVAILABLE_THEMES.map((t) => (
          <option key={t} value={t} className="capitalize">{t}</option>
        ))}
      </select>
    </div>
  )
}

