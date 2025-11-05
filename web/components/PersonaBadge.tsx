'use client';

import React from 'react';

export function PersonaBadge({ icon = '🌱', title, description, color }: { icon?: string; title: string; description?: string; color?: string; }) {
  return (
    <div className="card" style={{ borderLeft: `4px solid ${color || '#A8DADC'}` }}>
      <div style={{ fontSize: 20, fontWeight: 700 }}>{icon} {title}</div>
      {description ? <div style={{ color: 'var(--muted)', marginTop: 6 }}>{description}</div> : null}
    </div>
  );
}

