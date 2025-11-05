'use client'

import React from 'react'
import { useRecs } from '../../lib/hooks'
import { UserSwitcher } from '../../components/UserSwitcher'
import { RecommendationCard } from '../../components/RecommendationCard'
import { Card } from '../../components/ui/card'

export default function LearnPage() {
  const [userId, setUserId] = React.useState<string | undefined>();
  React.useEffect(() => {
    const saved = typeof window !== 'undefined' ? window.localStorage.getItem('userId') : null;
    if (saved) setUserId(saved);
  }, []);

  const { data } = useRecs(userId);

  return (
    <div className="grid gap-4">
      <Card className="flex items-center justify-between gap-3 p-3">
        <div>
          <div className="text-lg font-bold">📚 Learning Feed</div>
          <div className="text-muted-foreground">Educational content and personalized insights</div>
        </div>
        <UserSwitcher value={userId} onChange={(id) => { setUserId(id); window.localStorage.setItem('userId', id) }} />
      </Card>

      <div>
        {(data?.recommendations || []).map((rec) => (
          <RecommendationCard key={rec.recommendation_id} rec={rec} />
        ))}
      </div>
    </div>
  );
}
