"use client";
import { useParams } from "next/navigation";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { GlassPanel } from "@/components/layout/GlassPanel";
import { SlideUp } from "@/components/animations/SlideUp";
import { GlassLoader } from "@/components/common/GlassLoader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { useAssetDetails } from "@/lib/hooks/useAssets";

export default function AssetDetailPage() {
  const params = useParams<{ assetId: string }>();
  const assetId = decodeURIComponent(params?.assetId ?? "");
  const { data: versions, error, isLoading, mutate } = useAssetDetails(assetId || null);

  const latest = versions?.[0];

  return (
    <div>
      <GradientHeader
        title={latest?.name || assetId || "Asset"}
        subtitle={`Asset ID: ${assetId}`}
      />

      {isLoading && <GlassLoader />}
      {error && (
        <ErrorDisplay message={error.message} onRetry={() => mutate()} />
      )}

      {!isLoading && !error && versions && versions.length === 0 && (
        <EmptyState
          title="No versions found"
          message="This asset has no recorded versions yet."
        />
      )}

      {latest && (
        <GlassPanel animate delay={0.1} className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">
            Latest Version
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-[var(--text-secondary)] uppercase">
                Name
              </p>
              <p className="text-white font-medium">{latest.name}</p>
            </div>
            <div>
              <p className="text-xs text-[var(--text-secondary)] uppercase">
                System Time
              </p>
              <p className="text-white font-medium">
                {new Date(latest.system_time).toLocaleString()}
              </p>
            </div>
            <div className="col-span-2">
              <p className="text-xs text-[var(--text-secondary)] uppercase">
                Description
              </p>
              <p className="text-white">
                {latest.description || "No description"}
              </p>
            </div>
            <div className="col-span-2">
              <p className="text-xs text-[var(--text-secondary)] uppercase mb-2">
                Attributes
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(latest.attributes || {}).map(([k, v]) => (
                  <span
                    key={k}
                    className="text-xs px-3 py-1 rounded-full glass border border-white/10"
                  >
                    {k}: {v}
                  </span>
                ))}
                {Object.keys(latest.attributes || {}).length === 0 && (
                  <span className="text-xs text-[var(--text-secondary)]">
                    None
                  </span>
                )}
              </div>
            </div>
          </div>
        </GlassPanel>
      )}

      {versions && versions.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">
            Version History
          </h2>
          <div className="relative">
            <div className="absolute left-6 top-0 bottom-0 w-[2px] bg-gradient-to-b from-accent-purple to-accent-pink" />
            <div className="space-y-4">
              {versions.map((v, i) => (
                <SlideUp key={`${v.system_time}-${i}`} delay={i * 0.1}>
                  <div className="ml-12 relative">
                    <div className="absolute -left-[30px] top-4 w-3 h-3 rounded-full bg-accent-purple border-2 border-[var(--bg-gradient-start)]" />
                    <GlassPanel>
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="text-sm font-semibold text-white">
                            {v.name}
                          </p>
                          <p className="text-xs text-[var(--text-secondary)] mt-1">
                            {v.description}
                          </p>
                        </div>
                        <span className="text-xs text-[var(--text-secondary)]">
                          {new Date(v.system_time).toLocaleString()}
                        </span>
                      </div>
                    </GlassPanel>
                  </div>
                </SlideUp>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
