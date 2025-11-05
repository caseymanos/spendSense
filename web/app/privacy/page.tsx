'use client'

import React from 'react'
import { useProfile, useSetConsent } from '../../lib/hooks'
import { UserSwitcher } from '../../components/UserSwitcher'
import { Button } from '../../components/ui/button'
import { Card } from '../../components/ui/card'

export default function PrivacyPage() {
  const [userId, setUserId] = React.useState<string | undefined>();
  React.useEffect(() => {
    const saved = typeof window !== 'undefined' ? window.localStorage.getItem('userId') : null;
    if (saved) setUserId(saved);
  }, []);

  const { data: profile } = useProfile(userId);
  const setConsent = useSetConsent();

  const toggleConsent = () => {
    if (!userId) return;
    setConsent.mutate({ userId, granted: !profile?.consent_granted });
  };

  return (
    <div className="grid gap-4">
      <Card className="flex items-center justify-between gap-3 p-3">
        <div>
          <div className="text-lg font-bold">🔒 Privacy & Consent</div>
          <div className="text-muted-foreground">Manage your consent settings</div>
        </div>
        <UserSwitcher value={userId} onChange={(id) => { setUserId(id); window.localStorage.setItem('userId', id) }} />
      </Card>

      <Card className="p-3">
        <div className="mb-2 font-bold">{profile?.consent_granted ? '✓ Consent Active' : '✗ Consent Not Granted'}</div>
        <Button variant={profile?.consent_granted ? 'outline' : 'default'} onClick={toggleConsent}>
          {profile?.consent_granted ? 'Revoke Consent' : 'Grant Consent'}
        </Button>
      </Card>
    </div>
  )
}
