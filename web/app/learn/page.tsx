'use client';

import React from 'react';
import { useRecs } from '../../lib/hooks';
import { UserSwitcher } from '../../components/UserSwitcher';
import { RecommendationCard } from '../../components/RecommendationCard';

export default function LearnPage() {
  const [userId, setUserId] = React.useState<string | undefined>();
  React.useEffect(() => {
    const saved = typeof window !== 'undefined' ? window.localStorage.getItem('userId') : null;
    if (saved) setUserId(saved);
  }, []);

  const { data } = useRecs(userId);

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div className="card" style={{ display: 'flex', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 18 }}>📚 Learning Feed</div>
          <div style={{ color: 'var(--muted)' }}>Educational content and personalized insights</div>
        </div>
        <UserSwitcher value={userId} onChange={(id) => { setUserId(id); window.localStorage.setItem('userId', id); }} />
      </div>

      <div>
        {(data?.recommendations || []).map((rec) => (
          <RecommendationCard key={rec.recommendation_id} rec={rec} />
        ))}
      </div>
    </div>
  );
}

