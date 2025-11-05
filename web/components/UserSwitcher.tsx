'use client'

import React from 'react'
import { useUsers } from '../lib/hooks'

export function UserSwitcher({ value, onChange }: { value?: string; onChange: (id: string) => void }) {
  const { data: users } = useUsers()
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-9 rounded-md border bg-background px-3 text-sm"
    >
      <option value="">Select user…</option>
      {(users || []).map((u) => (
        <option key={u.user_id} value={u.user_id}>
          {u.consent_granted ? '✓' : '✗'} {u.name} ({u.user_id})
        </option>
      ))}
    </select>
  )
}
