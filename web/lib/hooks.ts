'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from './api';
import type { UserSummary, UserProfile, RecommendationsResponse, ConsentUpdateResponse } from './types';

export function useUsers() {
  return useQuery<UserSummary[]>({ queryKey: ['users'], queryFn: api.users });
}

export function useProfile(userId?: string) {
  return useQuery<UserProfile>({ queryKey: ['profile', userId], queryFn: () => api.profile(userId!), enabled: !!userId });
}

export function useRecs(userId?: string) {
  return useQuery<RecommendationsResponse>({ queryKey: ['recs', userId], queryFn: () => api.recs(userId!), enabled: !!userId });
}

export function useSetConsent() {
  const qc = useQueryClient();
  return useMutation<ConsentUpdateResponse, Error, { userId: string; granted: boolean }>({
    mutationFn: ({ userId, granted }) => api.setConsent(userId, granted),
    onSuccess: (_res, vars) => {
      qc.invalidateQueries({ queryKey: ['users'] });
      qc.invalidateQueries({ queryKey: ['profile', vars.userId] });
      qc.invalidateQueries({ queryKey: ['recs', vars.userId] });
    }
  });
}

