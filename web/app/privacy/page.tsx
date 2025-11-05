'use client';

import React from 'react';
import { useProfile, useSetConsent } from '../../lib/hooks';
import { UserSwitcher } from '../../components/UserSwitcher';

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
    <div style={{ display: 'grid', gap: 16 }}>
      <div className="card" style={{ display: 'flex', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: 18 }}>🔒 Privacy & Consent</div>
          <div style={{ color: 'var(--muted)' }}>Manage your consent settings</div>
        </div>
        <UserSwitcher value={userId} onChange={(id) => { setUserId(id); window.localStorage.setItem('userId', id); }} />
      </div>

      <div className="card">
        <div style={{ fontWeight: 700, marginBottom: 8 }}>{profile?.consent_granted ? '✓ Consent Active' : '✗ Consent Not Granted'}</div>
        <button className={profile?.consent_granted ? 'btn-outline' : 'btn'} onClick={toggleConsent}>
          {profile?.consent_granted ? 'Revoke Consent' : 'Grant Consent'}
        </button>
      </div>
    </div>
  );
}

