export interface Recommendation {
  rank: number;
  name: string;
  cuisine: string;
  rating: number;
  rating_str: string;
  cost: number;
  cost_str: string;
  explanation: string;
  medal: string;
  match_score: number;
  photo_url?: string;
  location?: string;
  distance?: string;
  reviews_count?: number;
  category?: string;
  acoustic_profile?: string;
  sensory_badges?: string[];
  daylight?: string;
  verified?: boolean;
}

export interface UserPreferences {
  location: string;
  budget: string;
  cuisines: string[];
  min_rating: number;
  extras: string;
}

export interface RecommendationResponse {
  success: boolean;
  count: number;
  recommendations: Recommendation[];
  query: UserPreferences;
}

export interface SystemMetadata {
  total_records: number;
  top_locations: string[];
  all_locations?: string[];
  model?: string;
  llm_provider?: string;
  dataset?: string;
  common_cuisines: string[];
  budget_tiers: { id: string; label: string; range: string }[];
  max_candidates: number;
  max_recommendations: number;
}
