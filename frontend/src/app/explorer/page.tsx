"use client";
import { useState, useCallback, useEffect } from "react";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { GlassPanel } from "@/components/layout/GlassPanel";
import { GlassSelect } from "@/components/forms/GlassSelect";
import { GlassDatePicker } from "@/components/forms/GlassDatePicker";
import { GradientLineChart } from "@/components/data/GradientLineChart";
import { AnimatedDataTable } from "@/components/data/AnimatedDataTable";
import { GlassLoader } from "@/components/common/GlassLoader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { FadeIn } from "@/components/animations/FadeIn";
import { useAssets } from "@/lib/hooks/useAssets";
import { useDataSources } from "@/lib/hooks/useDataSources";
import { useTimeSeries } from "@/lib/hooks/useTimeSeries";

/** Returns YYYY-MM-DD string for a Date. */
function toISODate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** Default dates: last 1 year from today. */
function getDefaultDates() {
  const end = new Date();
  const start = new Date();
  start.setFullYear(start.getFullYear() - 1);
  return { start: toISODate(start), end: toISODate(end) };
}

export default function ExplorerPage() {
  const defaults = getDefaultDates();
  const [assetId, setAssetId] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [startDate, setStartDate] = useState(defaults.start);
  const [endDate, setEndDate] = useState(defaults.end);
  const [fetchTrigger, setFetchTrigger] = useState(0);

  const { data: assetsData } = useAssets(0, 100);
  const { data: sourcesData } = useDataSources(0, 100);

  // Reset trigger when params change so stale data clears
  useEffect(() => {
    setFetchTrigger(0);
  }, [assetId, sourceId, startDate, endDate]);

  const shouldFetch = fetchTrigger > 0;

  const {
    data: tsData,
    error,
    isLoading,
    mutate,
  } = useTimeSeries(
    shouldFetch ? assetId : null,
    shouldFetch ? sourceId : null,
    shouldFetch ? startDate : null,
    shouldFetch ? endDate : null,
    true,
  );

  const handleFetch = useCallback(() => {
    setFetchTrigger((n) => n + 1);
  }, []);

  const assetOptions = (assetsData?.items || []).map((id) => ({
    value: id,
    label: id,
  }));
  const sourceOptions = (sourcesData?.items || []).map((id) => ({
    value: id,
    label: id,
  }));

  const chartData =
    tsData?.data?.records
      ?.map((r) => ({
        date: r.businessDate,
        value:
          typeof r.values.Close === "number"
            ? r.values.Close
            : typeof r.values.close === "number"
              ? r.values.close
              : 0,
      }))
      .reverse() ?? [];

  const tableColumns = tsData?.attributes ?? ["businessDate"];
  const tableRows =
    tsData?.data?.records?.map((r) => ({
      businessDate: r.businessDate,
      ...Object.fromEntries(
        Object.entries(r.values).map(([k, v]) => [k, String(v)]),
      ),
    })) ?? [];

  return (
    <div>
      <GradientHeader
        title="Data Explorer"
        subtitle="Query and visualize time-series data across assets and sources"
      />

      <GlassPanel className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
          <GlassSelect
            label="Asset"
            value={assetId}
            onChange={setAssetId}
            options={assetOptions}
            placeholder="Select asset..."
          />
          <GlassSelect
            label="Data Source"
            value={sourceId}
            onChange={setSourceId}
            options={sourceOptions}
            placeholder="Select source..."
          />
          <GlassDatePicker
            label="Start Date"
            value={startDate}
            onChange={setStartDate}
          />
          <GlassDatePicker
            label="End Date"
            value={endDate}
            onChange={setEndDate}
          />
          <button
            onClick={handleFetch}
            disabled={!assetId || !sourceId}
            className="gradient-btn py-2.5 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Fetch Data
          </button>
        </div>
      </GlassPanel>

      {isLoading && <GlassLoader />}
      {error && (
        <ErrorDisplay message={error.message} onRetry={() => mutate()} />
      )}

      {chartData.length > 0 && (
        <FadeIn>
          <GlassPanel className="mb-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              Price Chart
            </h2>
            <GradientLineChart data={chartData} height={400} />
          </GlassPanel>
        </FadeIn>
      )}

      {tableRows.length > 0 && (
        <FadeIn delay={0.2}>
          <GlassPanel>
            <h2 className="text-lg font-semibold text-white mb-4">
              Records ({tableRows.length})
            </h2>
            <AnimatedDataTable
              columns={["businessDate", ...tableColumns]}
              rows={tableRows}
            />
          </GlassPanel>
        </FadeIn>
      )}

      {shouldFetch && !isLoading && !error && chartData.length === 0 && (
        <EmptyState
          title="No records found"
          message="Try adjusting your date range or selecting a different asset."
        />
      )}
    </div>
  );
}
