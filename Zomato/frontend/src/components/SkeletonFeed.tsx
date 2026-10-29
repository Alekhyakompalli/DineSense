"use client";

import React from "react";

export default function SkeletonFeed() {
  return (
    <div className="flex flex-col space-y-space-md animate-pulse">
      {/* Simulation status pill */}
      <div className="p-space-md rounded-xl bg-surface-container-low text-on-surface-variant font-label-sm flex items-center gap-2 border border-white/[0.04]">
        <span className="material-symbols-outlined text-secondary text-[18px] animate-spin">
          cyclone
        </span>
        <span>Simulating live multimodal ingestion &amp; sensory vector calculation...</span>
      </div>

      {/* Skeleton Card 1 */}
      <div className="rounded-xl bg-surface-container p-space-lg shadow-xl space-y-4 border border-white/[0.04]">
        <div className="flex justify-between items-center">
          <div className="h-6 w-48 rounded bg-surface-container-highest"></div>
          <div className="h-6 w-16 rounded bg-surface-container-highest"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-5 h-44 rounded bg-surface-container-highest"></div>
          <div className="md:col-span-7 space-y-3">
            <div className="h-6 w-3/4 rounded bg-surface-container-highest"></div>
            <div className="h-4 w-1/2 rounded bg-surface-container-highest"></div>
            <div className="h-4 w-5/6 rounded bg-surface-container-highest"></div>
          </div>
        </div>
        <div className="h-20 rounded-xl bg-surface-container-highest/60"></div>
      </div>

      {/* Skeleton Card 2 */}
      <div className="rounded-xl bg-surface-container p-space-lg shadow-xl space-y-4 border border-white/[0.04]">
        <div className="flex justify-between items-center">
          <div className="h-6 w-40 rounded bg-surface-container-highest"></div>
          <div className="h-6 w-16 rounded bg-surface-container-highest"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-5 h-44 rounded bg-surface-container-highest"></div>
          <div className="md:col-span-7 space-y-3">
            <div className="h-6 w-2/3 rounded bg-surface-container-highest"></div>
            <div className="h-4 w-1/3 rounded bg-surface-container-highest"></div>
          </div>
        </div>
        <div className="h-16 rounded-xl bg-surface-container-highest/60"></div>
      </div>

      {/* Skeleton Card 3 */}
      <div className="rounded-xl bg-surface-container p-space-lg shadow-xl space-y-4 border border-white/[0.04]">
        <div className="flex justify-between items-center">
          <div className="h-6 w-44 rounded bg-surface-container-highest"></div>
          <div className="h-6 w-16 rounded bg-surface-container-highest"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-5 h-44 rounded bg-surface-container-highest"></div>
          <div className="md:col-span-7 space-y-3">
            <div className="h-6 w-3/5 rounded bg-surface-container-highest"></div>
            <div className="h-4 w-2/5 rounded bg-surface-container-highest"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

