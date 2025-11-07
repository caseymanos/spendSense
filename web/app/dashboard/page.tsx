'use client'

import React from 'react'
import { useProfile, useRecs } from '../../lib/hooks'
import { UserSwitcher } from '../../components/UserSwitcher'
import { MetricCard } from '../../components/MetricCard'
import { PersonaBadge } from '../../components/PersonaBadge'
import { Card } from '../../components/ui/card'
import { RecommendationCard } from '../../components/RecommendationCard'

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
    <div className="grid gap-4">
      <Card className="flex items-center justify-between gap-3 p-3">
        <div>
          <div className="text-lg font-bold">🏠 Your Financial Dashboard</div>
          <div className="text-muted-foreground">{profile ? `Welcome back, ${profile.name}` : 'Select a user to begin'}</div>
        </div>
        <UserSwitcher value={userId} onChange={onChangeUser} />
      </Card>

      {profile?.consent_granted ? (
        <>
          <PersonaBadge title={personaTitle} description="Your current persona" />
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <MetricCard label="Credit Cards" value={String(profile?.signals?.credit_num_cards ?? '0')} help="Active accounts" />
            <MetricCard label="Subscriptions" value={String(profile?.signals?.sub_180d_recurring_count ?? '0')} help="Recurring services" />
            <MetricCard label="Savings (6mo)" value={`$${Number(profile?.signals?.sav_180d_net_inflow ?? 0).toLocaleString()}`} help="Net inflow" />
          </div>
          <Card className="p-3">
            <div className="font-bold">Your Recommendations</div>
            {(recs?.recommendations || []).slice(0, 3).map((r) => (
              <RecommendationCard key={r.recommendation_id} rec={r} />
            ))}
          </Card>
        </>
      ) : (
        <Card className="border-yellow-300 bg-yellow-50 p-3">
          <div className="font-bold">Consent Not Yet Granted</div>
          <div>To provide personalized insights, please grant consent on the Privacy page.</div>
        </Card>
      )}
    </div>
  );
}
