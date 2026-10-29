"use client";

import React from "react";

interface HeaderProps {
  totalRecords?: number;
  engineName?: string;
  modelName?: string;
}

export default function Header({
  totalRecords = 12140,
  engineName = "Bangalore Food Engine v2.4",
  modelName = "Gemini 2.5 Flash",
}: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/80 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.4)] border-b border-white/[0.04]">
      {/* Top Bar */}
      <div className="h-16 w-full px-margin-mobile md:px-margin-tablet lg:px-margin flex items-center justify-between gap-gutter">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-space-md shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-container to-on-primary flex items-center justify-center shadow-lg shadow-primary-container/20">
              <span className="material-symbols-outlined text-white text-[20px]">restaurant</span>
            </div>
            <div className="flex flex-col">
              <span className="font-headline-sm text-headline-sm text-on-surface tracking-tight leading-none">
                DineSense
              </span>
              <span className="font-label-sm text-label-sm text-on-surface-variant tracking-wider uppercase">
                Sensory Intelligence
              </span>
            </div>
          </div>
        </div>

        {/* Center: Active Engine Capsule */}
        <div className="hidden lg:flex items-center gap-space-md flex-1 max-w-xl mx-auto">
          <div className="w-full flex items-center gap-space-sm px-space-md py-1.5 rounded-full bg-surface-container-high/60 shadow-[0_0_12px_rgba(0,0,0,0.2)] border border-white/[0.06]">
            <span className="material-symbols-outlined text-primary text-[18px]">radar</span>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
              Active Engine:
            </span>
            <span className="font-label-md text-label-md text-on-surface font-semibold">
              {engineName}
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-tertiary ml-auto animate-pulse"></span>
          </div>
        </div>

        {/* Right Stats & Badges */}
        <div className="flex items-center gap-space-sm shrink-0">
          {/* Gemini Model Indicator */}
          <div className="hidden md:flex items-center gap-2 px-space-md py-1 rounded-full bg-surface-container/70 border border-white/[0.04]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-label-md text-label-md text-on-surface">
              Powered by {modelName}
            </span>
          </div>

          {/* Dataset Records */}
          <div className="hidden xl:flex items-center gap-1.5 px-space-md py-1 rounded-full bg-surface-container-high/50 border border-white/[0.04]">
            <span className="material-symbols-outlined text-tertiary text-[16px]">database</span>
            <span className="font-label-md text-label-md text-on-surface font-medium">
              {totalRecords.toLocaleString()} Curated Restaurants
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
