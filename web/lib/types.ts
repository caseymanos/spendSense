export type UserSummary = {
  user_id: string;
  name: string;
  consent_granted: boolean;
};

export type UserProfile = {
  user_id: string;
  name: string;
  consent_granted: boolean;
  persona?: string | null;
  signals?: Record<string, any> | null;
};

export type Recommendation = {
  recommendation_id: string;
  type: 'education' | 'partner_offer';
  title: string;
  rationale: string;
  disclaimer: string;
};

export type RecommendationsResponse = {
  user_id: string;
  persona?: string | null;
  recommendations: Recommendation[];
  generated_at: string;
};

export type ConsentUpdateResponse = {
  success: boolean;
  user: UserSummary;
};

