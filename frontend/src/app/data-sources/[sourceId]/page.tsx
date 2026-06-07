"use client";
import { useParams } from "next/navigation";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { GlassPanel } from "@/components/layout/GlassPanel";
import { GlassLoader } from "@/components/common/GlassLoader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { useDataSourceDetails } from "@/lib/hooks/useDataSources";

export default function DataSourceDetailPage() {
  const params = useParams<{ sourceId: string }>();
  const sourceId = decodeURIComponent(params?.sourceId ?? "");
  const {
    data: versions,
    error,
    isLoading,
    mutate,
  } = useDataSourceDetails(sourceId || null);

  const latest = versions?.[0];

  return (
    <div>
      <GradientHeader
        title={latest?.name || sourceId || "Data Source"}
        subtitle={`Source ID: ${sourceId}`}
      />

      {isLoading && <GlassLoader />}
      {error && (
        <ErrorDisplay message={error.message} onRetry={() => mutate()} />
      )}

      {!isLoading && !error && versions && versions.length === 0 && (
        <EmptyState
          title="No versions found"
          message="This data source has no recorded versions yet."
        />
      )}

      {latest && (
        <GlassPanel animate delay={0.1} className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">
            Source Details
          </h2>
          <div className="space-y-4">
            <div>
              <p className="text-xs text-[var(--text-secondary)] uppercase">
                Name
              </p>
              <p className="text-white font-medium">{latest.name}</p>
            </div>
            <div>
              <p className="text-xs text-[var(--text-secondary)] uppercase">
                Description
              </p>
              <p className="text-white">
                {latest.description || "No description"}
              </p>
            </div>
            <div>
              <p className="text-xs text-[var(--text-secondary)] uppercase mb-2">
                Supported Attributes
              </p>
              <div className="flex flex-wrap gap-2">
                {latest.attributes?.map((attr) => (
                  <span
                    key={attr}
                    className="text-xs px-3 py-1 rounded-full bg-accent-blue/20 text-accent-blue border border-accent-blue/30"
                  >
                    {attr}
                  </span>
                ))}
                {(!latest.attributes || latest.attributes.length === 0) && (
                  <span className="text-xs text-[var(--text-secondary)]">
                    None
                  </span>
                )}
              </div>
            </div>
          </div>
        </GlassPanel>
      )}
    </div>
  );
}
