'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from './ui/button';
import { useTheme } from 'next-themes';

export function Header() {
  const { theme, setTheme } = useTheme();
  const next = theme === 'dark' ? 'light' : 'dark';

  return (
    <header className="flex items-center gap-4 border-b p-3">
      <div className="font-bold text-lg">💰 SpendSense</div>
      <nav className="flex gap-3">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/learn">Learning Feed</Link>
        <Link href="/privacy">Privacy</Link>
      </nav>
      <div className="ml-auto">
        <Button variant="outline" onClick={() => setTheme(next)}>
          {theme === 'dark' ? 'Light' : 'Dark'} Mode
        </Button>
      </div>
    </header>
  );
}
