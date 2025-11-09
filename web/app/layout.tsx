import './globals.css';
import React from 'react';
import { ReactQueryProvider } from '../providers/ReactQueryProvider';
import { HeaderNav } from '../components/HeaderNav';
import { PasswordGate } from '../components/PasswordGate';

export const metadata = {
  title: 'SpendSense Web',
  description: 'Consent-aware financial insights',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ReactQueryProvider>
          <PasswordGate>
            <HeaderNav />
            <main style={{ padding: 16, maxWidth: 1100, margin: '0 auto' }}>{children}</main>
          </PasswordGate>
        </ReactQueryProvider>
      </body>
    </html>
  );
}

