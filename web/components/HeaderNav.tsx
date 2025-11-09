'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LogoutButton } from './LogoutButton'

export function HeaderNav() {
  const pathname = usePathname()
  const isLoginPage = pathname === '/login'

  // Don't show header on login page
  if (isLoginPage) {
    return null
  }

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        padding: '12px 16px',
        borderBottom: '1px solid #e5e7eb',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ fontWeight: 700, fontSize: 18 }}>💰 SpendSense</div>
        <nav style={{ display: 'flex', gap: 12 }}>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/learn">Learning Feed</Link>
          <Link href="/privacy">Privacy</Link>
        </nav>
      </div>
      <LogoutButton />
    </header>
  )
}
