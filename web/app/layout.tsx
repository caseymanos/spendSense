import './globals.css';
import React from 'react';
import { ReactQueryProvider } from '../providers/ReactQueryProvider';
import Link from 'next/link';

export const metadata = {
  title: 'SpendSense Web',
  description: 'Consent-aware financial insights',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ReactQueryProvider>
          <header style={{ display: 'flex', gap: 16, padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>
            <div style={{ fontWeight: 700, fontSize: 18 }}>💰 SpendSense</div>
            <nav style={{ display: 'flex', gap: 12 }}>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/learn">Learning Feed</Link>
              <Link href="/privacy">Privacy</Link>
            </nav>
          </header>
          <main style={{ padding: 16, maxWidth: 1100, margin: '0 auto' }}>{children}</main>
        </ReactQueryProvider>
      </body>
    </html>
  );
}

