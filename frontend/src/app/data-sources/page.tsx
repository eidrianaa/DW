"use client";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { SourceGlassCard } from "@/components/cards/SourceGlassCard";
import { GlassLoader } from "@/components/common/GlassLoader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { useDataSources } from "@/lib/hooks/useDataSources";

export default function DataSourcesPage() {
  const { data, error, isLoading, mutate } = useDataSources(0, 100);

  return (
    <div>
      <GradientHeader
        title="Data Sources"
        subtitle="Connected data providers and their configuration"
      />

      {isLoading && <GlassLoader />}
      {error && (
        <ErrorDisplay message={error.message} onRetry={() => mutate()} />
      )}
      {!isLoading && !error && (!data?.items || data.items.length === 0) && (
        <EmptyState
          title="No data sources"
          message="Register a data source or run an ingestion to get started."
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.items?.map((id, i) => (
          <SourceGlassCard key={id} sourceId={id} delay={i * 0.1} />
        ))}
      </div>
    </div>
  );
}
