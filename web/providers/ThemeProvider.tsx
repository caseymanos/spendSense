'use client'

import * as React from 'react'
import { ThemeProvider as NextThemesProvider } from 'next-themes'

const THEMES = ['light', 'dark', 'glass', 'minimal', 'vibrant'] as const

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="light" enableSystem={false} themes={THEMES as unknown as string[]}>
      {children}
    </NextThemesProvider>
  )
}

export const AVAILABLE_THEMES = THEMES
