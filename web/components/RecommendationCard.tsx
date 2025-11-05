'use client';

import React from 'react';
import type { Recommendation } from '../lib/types';

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="card" style={{ marginTop: 12 }}>
      <div style={{ fontWeight: 600 }}>{rec.title}</div>
      <div style={{ marginTop: 4, color: 'var(--muted)' }}>{rec.rationale}</div>
    </div>
  );
}

