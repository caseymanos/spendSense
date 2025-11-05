'use client';

import React from 'react';

export function MetricCard({ label, value, help, color }: { label: string; value: string; help?: string; color?: string }) {
  return (
    <div className="card">
      <div style={{ fontSize: 12, color: 'var(--muted)' }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: color || 'var(--primary)' }}>{value}</div>
      {help ? <div style={{ fontSize: 12, color: 'var(--muted)' }}>{help}</div> : null}
    </div>
  );
}

