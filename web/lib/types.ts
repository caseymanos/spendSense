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
  content?: {
    type: string;
    data: any;
  };
  topic?: string;
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

export type Video = {
  video_id: string;
  youtube_id: string;
  title: string;
  channel_name?: string | null;
  duration_seconds?: number | null;
  thumbnail_url: string;
  description?: string | null;
  topic?: string;
};

