const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    cache: 'no-store',
    ...init,
  });
  if (!res.ok) {
    let msg = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${msg}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  users: () => request<import('./types').UserSummary[]>('/users'),
  profile: (id: string) => request<import('./types').UserProfile>(`/profile/${encodeURIComponent(id)}`),
  recs: (id: string) => request<import('./types').RecommendationsResponse>(`/recommendations/${encodeURIComponent(id)}`),
  setConsent: (id: string, granted: boolean) => request<import('./types').ConsentUpdateResponse>(`/consent`, { method: 'POST', body: JSON.stringify({ user_id: id, consent_granted: granted }) }),
  videos: (topic: string) => request<import('./types').Video[]>(`/videos/${encodeURIComponent(topic)}`),
  allVideos: () => request<import('./types').Video[]>('/videos'),
  videoTopics: () => request<string[]>('/videos/topics/list'),
};

