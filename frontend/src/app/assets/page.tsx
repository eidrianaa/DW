"use client";
import { useState } from "react";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { AssetGlassCard } from "@/components/cards/AssetGlassCard";
import { GlassLoader } from "@/components/common/GlassLoader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { GlassInput } from "@/components/forms/GlassInput";
import { useAssets } from "@/lib/hooks/useAssets";

function inferAssetType(id: string): "crypto" | "equity" {
  const upper = id.toUpperCase();
  // Check common crypto exchange prefixes or known crypto suffixes
  if (
    upper.includes("BITFINEX") ||
    upper.includes("BINANCE") ||
    upper.includes("COINBASE") ||
    upper.endsWith("USD") ||
    upper.endsWith("USDT") ||
    upper.endsWith("BTC")
  ) {
    return "crypto";
  }
  return "equity";
}

export default function AssetsPage() {
  const [search, setSearch] = useState("");
  const { data, error, isLoading, mutate } = useAssets(0, 100);

  const filteredItems =
    data?.items?.filter((id) =>
      id.toLowerCase().includes(search.toLowerCase()),
    ) ?? [];

  return (
    <div>
      <GradientHeader
        title="Financial Assets"
        subtitle="Browse and manage all registered financial instruments"
      />

      <div className="mb-6 max-w-md">
        <GlassInput
          placeholder="Search assets..."
          value={search}
          onChange={setSearch}
        />
      </div>

      {isLoading && <GlassLoader />}
      {error && (
        <ErrorDisplay message={error.message} onRetry={() => mutate()} />
      )}
      {!isLoading && !error && filteredItems.length === 0 && (
        <EmptyState
          title="No assets found"
          message="Try adjusting your search or ingest some data first."
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredItems.map((id, i) => (
          <AssetGlassCard
            key={id}
            assetId={id}
            name={id.split("/").pop() || id}
            type={inferAssetType(id)}
            delay={i * 0.05}
          />
        ))}
      </div>
    </div>
  );
}
