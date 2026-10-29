"use client";

import React from "react";
import { Recommendation, UserPreferences } from "@/types";
import RecommendationCard from "./RecommendationCard";
import SkeletonFeed from "./SkeletonFeed";

interface RecommendationFeedProps {
  recommendations: Recommendation[];
  preferences: UserPreferences;
  isLoading: boolean;
  onRelaxFilters?: () => void;
}

export default function RecommendationFeed({
  recommendations,
  preferences,
  isLoading,
  onRelaxFilters,
}: RecommendationFeedProps) {
  // Determine budget label display
  const getBudgetLabel = () => {
    switch (preferences.budget.toLowerCase()) {
      case "low":
        return "≤ ₹500";
      case "high":
        return "> ₹1,200";
      case "medium":
      default:
        return "₹500–₹1,200";
    }
  };

  const primaryLoc = preferences.location.split(",")[0].trim() || "Koramangala";
  const cuisineSummary =
    preferences.cuisines.length > 0
      ? preferences.cuisines.map((c) => c.charAt(0).toUpperCase() + c.slice(1)).join(" / ")
      : "Any Cuisine";

  return (
    <section className="lg:col-span-7 xl:col-span-8 flex flex-col space-y-space-md">
      {/* Header Row */}
      <div className="rounded-xl bg-surface-container-low p-space-md shadow-md flex flex-col md:flex-row md:items-center justify-between gap-space-sm border border-white/[0.04]">
        <div className="flex flex-col">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="font-headline-sm text-headline-sm text-on-surface">
              Top AI Matches for You
            </h2>
            <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary font-label-sm font-semibold">
              {recommendations.length} Handpicked Gems
            </span>
          </div>

          {/* Dynamic Filter Summary Pills */}
          <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
            <span className="font-label-sm text-on-surface-variant">Active Vectors:</span>
            <span className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface font-label-sm">
              {primaryLoc}
            </span>
            <span className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface font-label-sm">
              {getBudgetLabel()}
            </span>
            <span className="px-2 py-0.5 rounded bg-surface-container-highest text-tertiary font-label-sm">
              ★ {preferences.min_rating.toFixed(1)}+
            </span>
            <span className="px-2 py-0.5 rounded bg-surface-container-highest text-secondary font-label-sm">
              {cuisineSummary}
            </span>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <SkeletonFeed />
      ) : recommendations.length === 0 ? (
        /* Empty State */
        <div className="rounded-xl bg-surface-container p-space-xl text-center shadow-lg border border-white/[0.04]">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-surface-container-highest flex items-center justify-center">
            <span className="material-symbols-outlined text-[32px] text-tertiary">search_off</span>
          </div>
          <h3 className="font-headline-sm text-headline-sm text-on-surface mb-2">
            No Exact Matches in {primaryLoc}
          </h3>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto mb-6">
            Try adjusting your budget tier, lowering the minimum rating threshold, or broadening your
            target cuisine tags.
          </p>
          {onRelaxFilters && (
            <button
              type="button"
              onClick={onRelaxFilters}
              className="px-5 py-2.5 rounded-lg bg-primary-container text-on-primary font-label-md font-bold shadow-md hover:opacity-95 transition-all"
            >
              Auto-Relax Constraints &amp; Retry
            </button>
          )}
        </div>
      ) : (
        /* ================= FEED VIEW: ACTIVE RANKED RECOMMENDATIONS ================= */
        <div className="flex flex-col space-y-space-md">
          {/* Top 3 Major Feature Cards */}
          {recommendations.slice(0, 3).map((rec) => (
            <RecommendationCard key={rec.name + rec.rank} recommendation={rec} isCompact={false} />
          ))}

          {/* Cards 4 & 5 (Rendered as Sleek Compact 2-column Grid if present) */}
          {recommendations.length > 3 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
              {recommendations.slice(3).map((rec) => (
                <RecommendationCard
                  key={rec.name + rec.rank}
                  recommendation={rec}
                  isCompact={true}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

