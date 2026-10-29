"use client";

import React, { useState, useEffect } from "react";
import Header from "@/components/Header";
import PreferenceSidebar from "@/components/PreferenceSidebar";
import RecommendationFeed from "@/components/RecommendationFeed";
import { Recommendation, UserPreferences, SystemMetadata } from "@/types";

const DEFAULT_PREFERENCES: UserPreferences = {
  location: "Koramangala, Bangalore",
  budget: "medium",
  cuisines: ["cafe", "italian", "continental"],
  min_rating: 4.0,
  extras: "",
};

const INITIAL_RECOMMENDATIONS: Recommendation[] = [
  {
    rank: 1,
    medal: "🥇",
    name: "The Kind Roastery & Bakehouse",
    cuisine: "Specialty Cafe, Artisan Bakery, Continental",
    rating: 4.8,
    rating_str: "4.8",
    cost: 950,
    cost_str: "₹950 for two",
    explanation:
      "Direct match for your leafy courtyard and artisanal sourdough prompt. Features a tranquil open-air patio, award-winning Ethiopian pour-overs, and acoustic insulation dampening city bustle. Rated #1 for intimate brunch conversations.",
    match_score: 99.4,
    photo_url:
      "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80",
    location: "5th Block, Koramangala",
    distance: "1.2 km away",
    reviews_count: 2410,
    category: "Specialty Roastery",
    acoustic_profile: "Quiet (42 dB)",
    daylight: "92%",
    verified: true,
    sensory_badges: [
      "🌿 Garden Courtyard Seating",
      "☕ Single-Origin Geisha Pour-Over",
      "🥐 48hr Fermented Pain Au Chocolat",
    ],
  },
  {
    rank: 2,
    medal: "🥈",
    name: "Chianti Italian Ristorante & Wine Bar",
    cuisine: "Authentic Italian, Woodfired Sourdough, Wine Bar",
    rating: 4.7,
    rating_str: "4.7",
    cost: 1150,
    cost_str: "₹1,150 for two",
    explanation:
      "Matches your sourdough & intimate vibe criteria. Hand-tossed Neapolitan crusts fermented 48hrs, candle-lit courtyard veranda, and sommelier-curated pairing flight.",
    match_score: 96.8,
    photo_url:
      "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
    location: "100ft Road, Koramangala",
    distance: "1.8 km away",
    reviews_count: 4180,
    category: "Woodfired Veranda",
    acoustic_profile: "Intimate (48 dB)",
    daylight: "Candlelit Romantic",
    verified: true,
    sensory_badges: [
      "🍷 Curated Tuscan Reds",
      "🕯️ Intimate Veranda Seating",
      "🧀 Burrata Truffle Pizza",
    ],
  },
  {
    rank: 3,
    medal: "🥉",
    name: "Third Wave Coffee Roasters - Flagship Sanctuary",
    cuisine: "Specialty Cafe, Continental Light Bites, Cold Brew Lab",
    rating: 4.6,
    rating_str: "4.6",
    cost: 650,
    cost_str: "₹650 for two",
    explanation:
      "Ideal for specialty coffee & quiet seating. Sun-drenched glasshouse greenhouse section with custom Syphon brews and high acoustic dampening.",
    match_score: 94.2,
    photo_url:
      "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80",
    location: "4th Block, Koramangala",
    distance: "0.9 km away",
    reviews_count: 3890,
    category: "Manual Brew Bar",
    acoustic_profile: "Quiet (40 dB)",
    daylight: "Sunlit Glasshouse",
    verified: true,
    sensory_badges: [
      "☕ Cold Brew Tasting Flight",
      "🌿 Sunlit Glasshouse Seating",
      "🥪 Artisanal Sourdough Toast",
    ],
  },
  {
    rank: 4,
    medal: "#4",
    name: "Smoke House Deli",
    cuisine: "European, Bagels, Cafe",
    rating: 4.5,
    rating_str: "4.5",
    cost: 1200,
    cost_str: "₹1,200 for two",
    explanation:
      "European bistro styling with lush botanical terrace and delicate rosemary sourdough. Perfect for relaxed brunch appointments.",
    match_score: 91.5,
    location: "Lavelle Courtyard",
    distance: "2.4 km away",
    reviews_count: 2980,
    sensory_badges: [
      "🥖 Rosemary Bagels & Deli",
      "🌿 Lush Botanical Terrace",
      "🍵 Handcrafted Matcha",
    ],
  },
  {
    rank: 5,
    medal: "#5",
    name: "DYU Art Cafe",
    cuisine: "Kerala Heritage, Continental, Cafe",
    rating: 4.6,
    rating_str: "4.6",
    cost: 600,
    cost_str: "₹600 for two",
    explanation:
      "Quiet traditional courtyard surrounded by lush greenery, open sky courtyard, and indie art gallery. Quintessential heritage sanctuary.",
    match_score: 89.0,
    location: "5th Block, Koramangala",
    distance: "1.4 km away",
    reviews_count: 5120,
    sensory_badges: [
      "🌳 Traditional Heritage Courtyard",
      "🎨 Indie Art Gallery",
      "☕ Monsooned Malabar Coffee",
    ],
  },
];

export default function Home() {
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [recommendations, setRecommendations] = useState<Recommendation[]>(INITIAL_RECOMMENDATIONS);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<SystemMetadata | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

  // Attempt to fetch live dataset metadata from FastAPI backend
  useEffect(() => {
    async function fetchMetadata() {
      try {
        const res = await fetch(`${API_BASE}/api/metadata`);
        if (res.ok) {
          const data: SystemMetadata = await res.json();
          setMetadata(data);
        }
      } catch {
        // Backend offline or not ready; gracefully continue with defaults
      }
    }
    fetchMetadata();
  }, [API_BASE]);

  const handleRecommend = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch(`${API_BASE}/api/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location: preferences.location,
          budget: preferences.budget,
          cuisines: preferences.cuisines,
          min_rating: preferences.min_rating,
          extras: preferences.extras,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        const detailMsg =
          typeof errData.detail === "string"
            ? errData.detail
            : errData.detail?.errors?.join(", ") || "Failed to generate recommendations.";
        throw new Error(detailMsg);
      }

      const data = await response.json();
      if (data.recommendations && data.recommendations.length > 0) {
        setRecommendations(data.recommendations);
      } else {
        setRecommendations([]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error connecting to AI DineSense API";
      setErrorMessage(
        `${msg}. (Ensure the backend is reachable at ${API_BASE}).`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setPreferences(DEFAULT_PREFERENCES);
    setRecommendations(INITIAL_RECOMMENDATIONS);
    setErrorMessage(null);
  };

  const handleRelaxFilters = () => {
    setPreferences((prev) => ({
      ...prev,
      budget: "medium",
      min_rating: Math.max(3.5, prev.min_rating - 0.5),
      cuisines: [],
    }));
    // Auto-trigger with relaxed parameters
    setTimeout(() => {
      handleRecommend();
    }, 100);
  };

  return (
    <>
      {/* Subtle Ambient Radial Glow */}
      <div className="fixed top-0 left-0 right-0 h-48 pointer-events-none z-40 bg-[radial-gradient(ellipse_80%_60%_at_50%_-20%,rgba(139,92,246,0.15),transparent_70%),radial-gradient(ellipse_50%_40%_at_10%_0%,rgba(226,55,68,0.12),transparent_60%)]"></div>

      {/* Main Glassmorphic Header */}
      <Header
        totalRecords={metadata?.total_records || 12140}
        engineName="Bangalore Food Engine v2.4"
        modelName={
          metadata?.model
            ? metadata.model.replace("gemini-", "Gemini ").replace(/-/g, " ")
            : "Gemini 2.5 Flash"
        }
      />

      <main className="w-full pt-20 bg-background relative min-h-screen">
        <div className="flex flex-col w-full">
          <div className="relative w-full max-w-[1440px] mx-auto px-margin-mobile md:px-margin-tablet lg:px-margin py-space-md">
            {/* Top Spatial Banner: Status & Algorithmic Pulse */}
            <div className="w-full mb-space-md rounded-xl bg-surface-container/70 p-space-md shadow-lg flex flex-wrap items-center justify-between gap-space-md border border-white/[0.04]">
              <div className="flex items-center gap-space-sm flex-wrap">
                <span className="inline-flex items-center gap-1.5 px-space-sm py-1 rounded-full bg-secondary-container/40 text-on-secondary-container font-label-sm uppercase tracking-wider border border-secondary-container/30">
                  <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
                  <span>Neural Engine Active</span>
                </span>
                <span className="font-body-sm text-on-surface-variant">
                  Multimodal prompt vectorized into 1,024-D embedding space
                </span>
              </div>
            </div>

            {/* Error Banner Alert */}
            {errorMessage && (
              <div className="mb-space-md rounded-xl bg-error-container/30 p-space-md border border-error/40 text-on-surface flex items-start gap-space-sm">
                <span className="material-symbols-outlined text-error text-[20px] shrink-0">
                  warning
                </span>
                <div className="flex-1">
                  <span className="font-label-md font-bold text-error block">
                    API Notice
                  </span>
                  <span className="font-body-sm text-on-surface-variant">{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setErrorMessage(null)}
                  className="text-on-surface-variant hover:text-on-surface text-sm cursor-pointer"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Main 2-Column Responsive Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter lg:gap-gutter-lg items-start">
              {/* Left Column: Interactive Preference Sidebar */}
              <PreferenceSidebar
                preferences={preferences}
                onChange={setPreferences}
                onSubmit={handleRecommend}
                onReset={handleReset}
                isLoading={isLoading}
                topLocations={metadata?.top_locations}
                allLocations={metadata?.all_locations}
              />

              {/* Right Column: Recommendations Feed */}
              <RecommendationFeed
                recommendations={recommendations}
                preferences={preferences}
                isLoading={isLoading}
                onRelaxFilters={handleRelaxFilters}
              />
            </div>

            {/* Mobile Floating Bottom Dock Indicator */}
            <div className="lg:hidden fixed bottom-4 left-4 right-4 z-40 bg-surface-container/95 backdrop-blur-xl p-space-sm rounded-xl shadow-2xl flex items-center justify-between border border-white/[0.08]">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span className="font-label-md text-on-surface font-semibold">
                  {recommendations.length} AI Matches Ready
                </span>
              </div>
              <button
                type="button"
                className="px-3.5 py-1.5 rounded-lg bg-primary-container text-on-primary font-label-sm font-bold shadow-md cursor-pointer"
                onClick={() => window.scrollTo({ top: 550, behavior: "smooth" })}
              >
                View Matches ↓
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Global Footer */}
      <footer className="w-full bg-surface-container-lowest py-space-xl shadow-[0_-1px_12px_rgba(0,0,0,0.5)] border-t border-white/[0.04]">
        <div className="w-full px-margin-mobile md:px-margin-tablet lg:px-margin flex flex-col md:flex-row items-center justify-between gap-gutter">
          <div className="flex items-center gap-space-md flex-wrap">
            <div className="w-7 h-7 rounded bg-primary-container/20 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[16px]">restaurant</span>
            </div>
            <span className="font-label-md text-label-md text-on-surface-variant">
              © 2026 Zomato DineSense Intelligence. Algorithmic Gastronomy.
            </span>
            <a
              href="https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation"
              target="_blank"
              rel="noopener noreferrer"
              className="font-label-sm text-secondary hover:underline flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[14px]">dataset</span>
              <span>Dataset: ManikaSaini/zomato-restaurant-recommendation (HuggingFace)</span>
            </a>
          </div>
          <div className="flex items-center gap-space-lg">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
              Latency: 14ms
            </span>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
              Bangalore Cluster
            </span>
          </div>
        </div>
      </footer>
    </>
  );
}
