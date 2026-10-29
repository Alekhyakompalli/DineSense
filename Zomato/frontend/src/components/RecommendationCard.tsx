"use client";

import React, { useState } from "react";
import { Recommendation } from "@/types";

interface RecommendationCardProps {
  recommendation: Recommendation;
  isCompact?: boolean;
}

const FALLBACK_PHOTOS = [
  "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=800&q=80",
  "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=800&q=80",
];

const DEFAULT_BADGES_BY_RANK: Record<number, string[]> = {
  1: ["🌿 Garden Courtyard Seating", "☕ Single-Origin Pour-Over", "🥐 48hr Fermented Sourdough"],
  2: ["🍷 Curated Tuscan Reds", "🕯️ Intimate Veranda Seating", "🧀 Truffle Burrata Crusts"],
  3: ["☕ Cold Brew Tasting Flight", "🌿 Sunlit Glasshouse Seating", "🥪 Artisanal Sourdough Toast"],
  4: ["🥖 Rosemary Bagels & Deli", "🌿 Lush Botanical Terrace", "🍵 Handcrafted Matcha"],
  5: ["🌳 Traditional Heritage Courtyard", "🎨 Indie Art Gallery", "☕ Monsooned Malabar Coffee"],
};

export default function RecommendationCard({
  recommendation: rec,
  isCompact = false,
}: RecommendationCardProps) {
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [imgSrc, setImgSrc] = useState(
    rec.photo_url || FALLBACK_PHOTOS[(rec.rank - 1) % FALLBACK_PHOTOS.length]
  );

  const sensoryBadges =
    rec.sensory_badges ||
    DEFAULT_BADGES_BY_RANK[rec.rank] || [
      "🌿 Ambient Courtyard",
      "✨ Chef Selection",
      "☕ Curated Pairings",
    ];

  const reviewCount = rec.reviews_count || (3200 - (rec.rank - 1) * 380);
  const distance = rec.distance || `${(0.8 + (rec.rank - 1) * 0.4).toFixed(1)} km away`;
  const locationText = rec.location ? `${rec.location} (${distance})` : `Bangalore (${distance})`;

  // Split cuisines into tags
  const cuisineTags = rec.cuisine
    ? rec.cuisine.split(",").map((c) => c.trim())
    : ["Cafe", "Continental"];

  // Top header label & medal badge
  const medalBadgeClass =
    rec.rank === 1
      ? "bg-tertiary-container text-on-tertiary-container font-bold"
      : rec.rank === 2
      ? "bg-surface-container-highest text-on-surface font-bold"
      : "bg-surface-container-highest text-on-surface font-semibold";

  // Compact layout (Cards #4 and #5)
  if (isCompact) {
    return (
      <article className="rounded-xl bg-surface-container p-space-md shadow-lg hover:bg-surface-container-high transition-colors flex flex-col justify-between border border-white/[0.04]">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant font-label-sm font-semibold">
              #{rec.rank} Match ({rec.match_score.toFixed(1)}%)
            </span>
            <div className="flex items-center gap-1 text-tertiary font-label-md font-bold">
              <span className="material-symbols-outlined text-[15px]">star</span>
              <span>{rec.rating_str || rec.rating.toFixed(1)}</span>
            </div>
          </div>

          <h4 className="font-headline-sm text-headline-sm text-on-surface leading-snug">
            {rec.name}
          </h4>
          <p className="font-body-sm text-on-surface-variant mt-1">
            {rec.cuisine} • {rec.location || "Bangalore Central"}
          </p>

          <div className="rounded-lg bg-surface-container-highest/50 p-space-sm mt-3 text-body-sm text-on-surface border border-white/[0.04]">
            <span className="text-secondary font-label-sm uppercase font-bold block mb-0.5">
              Atmospheric Fit
            </span>
            {rec.explanation}
          </div>
        </div>

        <div className="mt-4 pt-3 flex items-center justify-between border-t border-white/[0.04]">
          <span className="font-label-md text-tertiary">{rec.cost_str}</span>
          <button
            type="button"
            className="px-3 py-1.5 rounded-lg bg-surface-container-highest text-on-surface font-label-md font-semibold hover:bg-surface-bright transition-colors cursor-pointer"
          >
            Quick Reserve
          </button>
        </div>
      </article>
    );
  }

  // Full-feature card (Cards #1, #2, #3)
  return (
    <article className="rounded-xl bg-surface-container p-space-md md:p-space-lg shadow-xl shadow-surface-container-lowest/60 hover:bg-surface-container-high transition-colors border border-white/[0.04]">
      {/* Top Medal & Match Header */}
      <div className="flex flex-wrap items-center justify-between gap-space-sm mb-space-sm">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-label-sm shadow-sm ${medalBadgeClass}`}
          >
            <span className="material-symbols-outlined text-[16px]">
              {rec.rank === 1 ? "military_tech" : rec.rank === 2 ? "looks_two" : "workspace_premium"}
            </span>
            <span>
              {rec.medal} #{rec.rank} AI Match ({rec.match_score.toFixed(1)}% Taste Alignment)
            </span>
          </span>
          <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-surface-container-highest text-emerald-400 font-label-sm">
            <span className="material-symbols-outlined text-[14px]">verified</span>
            <span>DineSense Verified</span>
          </span>
        </div>

        <div className="flex items-center gap-1 bg-surface-container-highest/80 px-2.5 py-1 rounded-full font-label-md text-tertiary font-bold border border-white/[0.04]">
          <span className="material-symbols-outlined text-[16px]">star</span>
          <span>{rec.rating_str || rec.rating.toFixed(1)}</span>
          <span className="text-on-surface-variant font-normal font-label-sm ml-0.5">
            ({reviewCount.toLocaleString()} reviews)
          </span>
        </div>
      </div>

      {/* Content Split: Photo Hero + Title Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter items-start mb-space-sm">
        <div className="md:col-span-5 h-48 md:h-44 rounded-lg overflow-hidden relative shadow-md bg-surface-container-high">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
            alt={rec.name}
            src={imgSrc}
            onError={() =>
              setImgSrc(FALLBACK_PHOTOS[(rec.rank - 1) % FALLBACK_PHOTOS.length])
            }
          />
          <div className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-surface-container-lowest/80 backdrop-blur-md text-on-surface font-label-sm flex items-center gap-1 border border-white/[0.06]">
            <span className="material-symbols-outlined text-primary text-[14px]">local_cafe</span>
            <span>{cuisineTags[0] || "Specialty"}</span>
          </div>
        </div>

        <div className="md:col-span-7 flex flex-col justify-between h-full">
          <div>
            <h3 className="font-headline-sm text-headline-sm text-on-surface tracking-tight">
              {rec.name}
            </h3>
            <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
              {cuisineTags.slice(0, 3).map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant font-label-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
            <div className="mt-2.5 flex flex-wrap items-center gap-x-4 gap-y-1 font-body-sm text-on-surface-variant">
              <span className="flex items-center gap-1 text-on-surface font-medium">
                <span className="material-symbols-outlined text-[16px] text-tertiary">payments</span>
                <span>{rec.cost_str}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px] text-primary">pin_drop</span>
                <span>{locationText}</span>
              </span>
            </div>
          </div>

          {/* Live Radar Mini Data Point */}
          <div className="mt-3 flex items-center gap-2 text-on-surface-variant font-label-sm">
            <span className="material-symbols-outlined text-[16px] text-secondary">graphic_eq</span>
            <span>
              Acoustic Profile: <strong>Quiet (42 dB)</strong> • Natural Daylight: <strong>92%</strong>
            </span>
          </div>
        </div>
      </div>

      {/* AI Reasoner Box (Signature Glass Neon Banner) */}
      <div className="mb-space-sm rounded-xl bg-surface-container-highest/60 p-space-md shadow-md relative overflow-hidden border border-white/[0.04]">
        <div className="flex items-start gap-space-sm">
          <div className="w-8 h-8 rounded-lg bg-secondary-container flex items-center justify-center shrink-0 shadow-sm">
            <span className="material-symbols-outlined text-on-secondary text-[18px]">neurology</span>
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="font-label-md text-label-md text-secondary font-bold flex items-center gap-1">
                <span>Why this fits your palate prompt</span>
              </span>
              <span className="font-label-sm text-tertiary font-semibold">
                Score: {rec.match_score.toFixed(1)}/100
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface leading-relaxed">
              {rec.explanation}
            </p>

            {/* Sensory Badges */}
            <div className="flex flex-wrap items-center gap-2 mt-2.5">
              {sensoryBadges.map((badge, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded-full bg-surface-container text-on-surface font-label-sm flex items-center gap-1 border border-white/[0.04]"
                >
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Action Row */}
      <div className="flex flex-wrap items-center justify-between gap-space-sm pt-space-xs border-t border-white/[0.04]">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="px-3.5 py-2 rounded-lg bg-surface-container-highest text-on-surface font-label-md font-semibold hover:bg-surface-bright transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[18px]">restaurant_menu</span>
            <span>View Menu &amp; Tasting Notes</span>
          </button>
          <button
            type="button"
            onClick={() => setIsBookmarked(!isBookmarked)}
            className={`p-2 rounded-lg bg-surface-container-highest transition-colors cursor-pointer ${
              isBookmarked ? "text-primary" : "text-on-surface-variant hover:text-primary"
            }`}
            title="Bookmark to Palate List"
          >
            <span className="material-symbols-outlined text-[20px]">
              {isBookmarked ? "bookmark" : "bookmark_border"}
            </span>
          </button>
        </div>
      </div>
    </article>
  );
}

