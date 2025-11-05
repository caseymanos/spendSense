'use client';

import React from 'react';
import { useProfile, useRecs } from '../../lib/hooks';
import { UserSwitcher } from '../../components/UserSwitcher';
import { MetricCard } from '../../components/MetricCard';
import { PersonaBadge } from '../../components/PersonaBadge';

export default function DashboardPage() {
  const [userId, setUserId] = React.useState<string | undefined>();
  const { data: profile } = useProfile(userId);
  const { data: recs } = useRecs(userId);

  React.useEffect(() => {
    // Attempt to load persisted user selection
    const saved = typeof window !== 'undefined' ? window.localStorage.getItem('userId') : null;
    if (saved) setUserId(saved);
  }, []);

  const onChangeUser = (id: string) => {
    setUserId(id);
    if (typeof window !== 'undefined') window.localStorage.setItem('userId', id);
  };

  const personaTitle = (profile?.persona || 'general').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div className="card" style={{ display: 'flex', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 18 }}>🏠 Your Financial Dashboard</div>
          <div style={{ color: 'var(--muted)' }}>{profile ? `Welcome back, ${profile.name}` : 'Select a user to begin'}</div>
        </div>
        <UserSwitcher value={userId} onChange={onChangeUser} />
      </div>

      {profile?.consent_granted ? (
        <>
          <PersonaBadge title={personaTitle} description="Your current persona" />
          <div className="grid-3">
            <MetricCard label="Credit Cards" value={String(profile?.signals?.credit_num_cards ?? '0')} help="Active accounts" />
            <MetricCard label="Subscriptions" value={String(profile?.signals?.sub_180d_recurring_count ?? '0')} help="Recurring services" />
            <MetricCard label="Savings (6mo)" value={`$${Number(profile?.signals?.sav_180d_net_inflow ?? 0).toLocaleString()}`} help="Net inflow" />
          </div>
          <div className="card">
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Your Recommendations</div>
            {(recs?.recommendations || []).slice(0, 3).map((r) => (
              <div key={r.recommendation_id} className="card" style={{ marginTop: 8 }}>
                <div style={{ fontWeight: 600 }}>{r.title}</div>
                <div style={{ marginTop: 4, color: 'var(--muted)' }}>{r.rationale}</div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="card" style={{ borderColor: 'var(--warning)', background: '#FEF3C7' }}>
          <div style={{ fontWeight: 700 }}>Consent Not Yet Granted</div>
          <div>To provide personalized insights, please grant consent on the Privacy page.</div>
        </div>
      )}
    </div>
  );
}

