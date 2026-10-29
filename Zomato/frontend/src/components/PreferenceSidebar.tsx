"use client";

import React, { useState } from "react";
import { UserPreferences } from "@/types";

interface PreferenceSidebarProps {
  preferences: UserPreferences;
  onChange: (prefs: UserPreferences) => void;
  onSubmit: () => void;
  onReset: () => void;
  isLoading: boolean;
  topLocations?: string[];
  allLocations?: string[];
}

const DEFAULT_LOCALITIES = [
  { label: "Koramangala", value: "Koramangala, Bangalore" },
  { label: "Indiranagar", value: "Indiranagar, Bangalore" },
  { label: "Lavelle Road", value: "Lavelle Road, Bangalore" },
  { label: "Whitefield", value: "Whitefield, Bangalore" },
  { label: "HSR Layout", value: "HSR, Bangalore" },
  { label: "Jayanagar", value: "Jayanagar, Bangalore" },
  { label: "Church Street", value: "Church Street, Bangalore" },
];

const FALLBACK_ALL_LOCATIONS = [
  "Banashankari",
  "Banaswadi",
  "Bannerghatta Road",
  "Basavanagudi",
  "Basaveshwara Nagar",
  "Bellandur",
  "Bommanahalli",
  "Brigade Road",
  "Brookefield",
  "BTM",
  "Central Bangalore",
  "Church Street",
  "Commercial Street",
  "Cunningham Road",
  "Domlur",
  "Electronic City",
  "Frazer Town",
  "HSR",
  "Indiranagar",
  "ITPL Main Road, Whitefield",
  "Jayanagar",
  "JP Nagar",
  "Kalyan Nagar",
  "Kammanahalli",
  "Koramangala 1st Block",
  "Koramangala 4th Block",
  "Koramangala 5th Block",
  "Koramangala 6th Block",
  "Koramangala 7th Block",
  "Lavelle Road",
  "Malleshwaram",
  "Marathahalli",
  "MG Road",
  "New BEL Road",
  "Old Airport Road",
  "Rajajinagar",
  "Residency Road",
  "Richmond Road",
  "Sarjapur Road",
  "Shanti Nagar",
  "St. Marks Road",
  "Ulsoor",
  "Vasanth Nagar",
  "Whitefield",
];

const CUISINE_OPTIONS = [
  { id: "cafe", label: "☕ Cafe" },
  { id: "italian", label: "🍕 Italian & Sourdough" },
  { id: "north indian", label: "🥘 North Indian" },
  { id: "continental", label: "🍷 Continental" },
  { id: "pan-asian", label: "🥢 Pan-Asian" },
  { id: "desserts", label: "🍰 Artisan Desserts" },
];

export default function PreferenceSidebar({
  preferences,
  onChange,
  onSubmit,
  onReset,
  isLoading,
  topLocations,
  allLocations,
}: PreferenceSidebarProps) {
  const [showAbout, setShowAbout] = useState(false);
  const [isManualInput, setIsManualInput] = useState(false);

  const locationsList =
    allLocations && allLocations.length > 0 ? allLocations : FALLBACK_ALL_LOCATIONS;

  const topHubsList =
    topLocations && topLocations.length > 0
      ? topLocations
      : [
          "Koramangala 5Th Block",
          "Indiranagar",
          "Koramangala 4Th Block",
          "Lavelle Road",
          "Whitefield",
          "Hsr",
          "Jayanagar",
          "Church Street",
          "Mg Road",
          "Btm",
        ];

  const handleLocationChange = (val: string) => {
    onChange({ ...preferences, location: val });
  };

  const handleBudgetChange = (tier: string) => {
    onChange({ ...preferences, budget: tier });
  };

  const handleRatingChange = (val: number) => {
    onChange({ ...preferences, min_rating: val });
  };

  const toggleCuisine = (cuisineId: string) => {
    const exists = preferences.cuisines.includes(cuisineId);
    const updated = exists
      ? preferences.cuisines.filter((c) => c !== cuisineId)
      : [...preferences.cuisines, cuisineId];
    onChange({ ...preferences, cuisines: updated });
  };

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

  return (
    <aside className="lg:col-span-5 xl:col-span-4 lg:sticky lg:top-24 z-20">
      <div className="rounded-xl bg-surface-container-low/95 p-space-lg shadow-xl shadow-surface-container-lowest/80 relative overflow-hidden backdrop-blur-2xl border border-white/[0.06]">
        {/* Decorative Top Ambient Mesh Accents */}
        <div className="absolute -top-16 -right-16 w-36 h-36 rounded-full bg-primary/10 blur-2xl pointer-events-none"></div>
        <div className="absolute -bottom-20 -left-20 w-44 h-44 rounded-full bg-secondary-container/20 blur-3xl pointer-events-none"></div>

        {/* Section Heading Badge */}
        <div className="relative z-10 mb-space-md">
          <div className="flex items-center justify-between">
            <span className="font-label-sm uppercase tracking-wider text-secondary font-bold">
              Neural Preference Matrix
            </span>
            <span className="font-label-sm text-tertiary px-2 py-0.5 rounded-full bg-tertiary-container/30 font-semibold">
              Auto-Refining
            </span>
          </div>
        </div>

        {/* Filter Form Controls */}
        <div className="space-y-space-md relative z-10">
          {/* 1. Location Dropdown & Input */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-label-md text-label-md text-on-surface flex items-center gap-1">
                <span>Discovery Epicenter</span>
                <span className="text-secondary font-semibold text-xs">• Dropdown Active</span>
              </label>
              <button
                type="button"
                onClick={() => setIsManualInput(!isManualInput)}
                className="text-primary hover:underline text-xs flex items-center gap-0.5 cursor-pointer"
              >
                <span className="material-symbols-outlined text-[14px]">
                  {isManualInput ? "list" : "edit"}
                </span>
                <span>{isManualInput ? "Use Dropdown" : "Type Custom"}</span>
              </button>
            </div>

            {/* Dropdown Select Menu */}
            {!isManualInput ? (
              <div className="relative flex items-center">
                <span className="material-symbols-outlined absolute left-3 text-primary text-[20px] pointer-events-none">
                  arrow_drop_down_circle
                </span>
                <select
                  value={preferences.location}
                  onChange={(e) => handleLocationChange(e.target.value)}
                  className="w-full h-11 pl-10 pr-9 rounded-lg bg-surface-container-highest text-on-surface font-body-md focus:outline-none focus:ring-1 focus:ring-primary border border-white/[0.08] cursor-pointer appearance-none shadow-inner"
                >
                  <option value="" disabled className="bg-surface-container-high text-on-surface-variant">
                    -- Select a Dining Locality --
                  </option>

                  {/* Top Popular Hubs */}
                  <optgroup label="✨ Top Bangalore Dining Hubs" className="bg-surface-container-high text-primary font-bold">
                    {topHubsList.map((hub) => (
                      <option
                        key={`top-${hub}`}
                        value={`${hub}, Bangalore`}
                        className="bg-surface-container-high text-on-surface font-medium"
                      >
                        {hub}
                      </option>
                    ))}
                  </optgroup>

                  {/* All 90+ Unique Localities */}
                  <optgroup label="🏙️ All Neighborhoods (A–Z)" className="bg-surface-container-high text-secondary font-bold">
                    {locationsList.map((loc) => (
                      <option
                        key={`all-${loc}`}
                        value={`${loc}, Bangalore`}
                        className="bg-surface-container-high text-on-surface font-normal"
                      >
                        {loc}
                      </option>
                    ))}
                  </optgroup>
                </select>
                <span className="material-symbols-outlined absolute right-3 text-on-surface-variant text-[20px] pointer-events-none">
                  expand_more
                </span>
              </div>
            ) : (
              /* Custom Text Input Mode */
              <div className="relative flex items-center">
                <span className="material-symbols-outlined absolute left-3 text-primary text-[20px] pointer-events-none">
                  location_on
                </span>
                <input
                  className="w-full h-11 pl-10 pr-4 rounded-lg bg-surface-container-highest text-on-surface font-body-md focus:outline-none focus:bg-surface-container-highest transition-colors shadow-inner border border-white/[0.08]"
                  placeholder="Type any neighborhood or street..."
                  type="text"
                  value={preferences.location}
                  onChange={(e) => handleLocationChange(e.target.value)}
                />
              </div>
            )}

            {/* Quick Locality Pills */}
            <div className="flex flex-wrap gap-1.5 mt-2">
              {DEFAULT_LOCALITIES.map((loc) => {
                const isSelected =
                  preferences.location.toLowerCase().includes(loc.label.toLowerCase()) ||
                  preferences.location.toLowerCase() === loc.value.toLowerCase();
                return (
                  <button
                    key={loc.label}
                    type="button"
                    onClick={() => handleLocationChange(loc.value)}
                    className={`px-2.5 py-1 rounded-full font-label-sm text-label-sm transition-all cursor-pointer ${
                      isSelected
                        ? "bg-primary-container text-on-primary font-semibold shadow-sm"
                        : "bg-surface-container-high text-on-surface-variant hover:text-on-surface"
                    }`}
                  >
                    {loc.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Budget Tier (Segmented Control) */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-label-md text-label-md text-on-surface">Budget Tier (For Two)</label>
              <span className="font-label-sm text-primary">{getBudgetLabel()}</span>
            </div>
            <div className="grid grid-cols-3 gap-1 p-1 rounded-lg bg-surface-container-highest/70 text-center border border-white/[0.04]">
              {[
                { id: "low", label: "Low (≤ ₹500)" },
                { id: "medium", label: "Med (₹500–₹1.2k)" },
                { id: "high", label: "High (> ₹1.2k)" },
              ].map((tier) => {
                const isSelected = preferences.budget.toLowerCase() === tier.id;
                return (
                  <button
                    key={tier.id}
                    type="button"
                    onClick={() => handleBudgetChange(tier.id)}
                    className={`py-2 px-1 rounded font-label-sm text-label-sm transition-all cursor-pointer ${
                      isSelected
                        ? "bg-primary-container text-on-primary font-semibold shadow-md"
                        : "text-on-surface-variant hover:text-on-surface"
                    }`}
                  >
                    {tier.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 3. Minimum Rating Slider */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="font-label-md text-label-md text-on-surface">Minimum DineSense Rating</label>
              <span className="flex items-center gap-1 font-label-md text-label-md px-2 py-0.5 rounded-full bg-tertiary-container text-on-tertiary-container font-bold">
                <span className="material-symbols-outlined text-[14px]">star</span>
                <span>{preferences.min_rating.toFixed(1)}+</span>
              </span>
            </div>
            <div className="px-1">
              <input
                className="w-full accent-primary h-1.5 bg-surface-container-highest rounded-lg cursor-pointer appearance-none"
                max="4.8"
                min="3.5"
                step="0.1"
                type="range"
                value={preferences.min_rating}
                onChange={(e) => handleRatingChange(parseFloat(e.target.value))}
              />
              <div className="flex justify-between font-label-sm text-label-sm text-on-surface-variant mt-1">
                <span>3.5</span>
                <span className="text-tertiary font-bold">4.0 (Default)</span>
                <span>4.5</span>
                <span>4.8</span>
              </div>
            </div>
          </div>

          {/* 4. Target Cuisines Multi-Select Chips */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-label-md text-label-md text-on-surface">Target Cuisines &amp; Profiling</label>
              <span className="font-label-sm text-secondary">
                {preferences.cuisines.length} Selected
              </span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {CUISINE_OPTIONS.map((c) => {
                const isSelected = preferences.cuisines.includes(c.id);
                return (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => toggleCuisine(c.id)}
                    className={`px-3 py-1.5 rounded-full font-label-sm text-label-sm transition-all cursor-pointer ${
                      isSelected
                        ? "bg-primary-container text-on-primary font-medium shadow-sm"
                        : "bg-surface-container-high text-on-surface-variant hover:text-on-surface"
                    }`}
                  >
                    {c.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Main Action Buttons: Generate & Reset */}
          <div className="flex flex-col gap-2 pt-2">
            <button
              type="button"
              disabled={isLoading}
              onClick={onSubmit}
              className="w-full py-3 px-space-md rounded-lg bg-primary-container text-on-primary font-label-lg font-bold shadow-lg shadow-primary-container/30 flex items-center justify-center gap-2 hover:opacity-95 active:scale-[0.99] transition-all disabled:opacity-60 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <span className="material-symbols-outlined text-[20px] animate-spin">refresh</span>
                  <span>Synthesizing Recommendations...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[20px]">rocket_launch</span>
                  <span>Generate AI Recommendations</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={onReset}
              className="w-full py-2 px-space-md rounded-lg bg-surface-container-highest text-on-surface-variant font-label-md hover:text-on-surface hover:bg-surface-bright transition-colors flex items-center justify-center gap-1.5 cursor-pointer border border-white/[0.04]"
            >
              <span className="material-symbols-outlined text-[16px]">restart_alt</span>
              <span>Reset Filters</span>
            </button>
          </div>

          {/* Realtime Engine Feedback Tag */}
          <div className="text-center font-label-sm text-on-surface-variant flex items-center justify-center gap-1.5 pt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Vector index ready: {primaryLoc} sensory profiles</span>
          </div>

          {/* About Expandable Card */}
          <div className="pt-2 border-t border-white/[0.06]">
            <button
              type="button"
              onClick={() => setShowAbout(!showAbout)}
              className="w-full flex items-center justify-between text-left font-label-sm text-secondary hover:underline cursor-pointer"
            >
              <span className="flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">info</span>
                <span>About DineSense Intelligence</span>
              </span>
              <span className="material-symbols-outlined text-[14px]">
                {showAbout ? "expand_less" : "expand_more"}
              </span>
            </button>
            {showAbout && (
              <div className="mt-2 p-3 rounded-lg bg-surface-container-highest/50 font-body-sm text-on-surface-variant space-y-1.5 text-xs leading-relaxed border border-white/[0.04]">
                <p>
                  <strong>DineSense</strong> is an AI-powered culinary intelligence platform that combines
                  structured restaurant data (12,140 verified dining spots) with Gemini LLM reasoning.
                </p>
                <p>
                  It evaluates location proximity, budget tiers, and cuisines to deliver top-ranked recommendations with personalized justifications.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
