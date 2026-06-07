"use client";
import { useState } from "react";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { GlassPanel } from "@/components/layout/GlassPanel";
import { GlassInput } from "@/components/forms/GlassInput";
import { GlassSelect } from "@/components/forms/GlassSelect";
import { GlassMetricCard } from "@/components/cards/GlassMetricCard";
import { AnimatedBarChart } from "@/components/data/AnimatedBarChart";
import { GradientLineChart } from "@/components/data/GradientLineChart";
import { AnimatedDataTable } from "@/components/data/AnimatedDataTable";
import { GlassLoader } from "@/components/common/GlassLoader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { FadeIn } from "@/components/animations/FadeIn";
import { useTotals, usePredictions, useAnomalies } from "@/lib/hooks/useAnalytics";
import { useAssets } from "@/lib/hooks/useAssets";
import { useDataSources } from "@/lib/hooks/useDataSources";
import { api, PredictionJobResult } from "@/lib/api";
import clsx from "clsx";

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<
    "aggregation" | "predictions" | "anomalies"
  >("aggregation");
  const [running, setRunning] = useState(false);
  const [jobError, setJobError] = useState<string | null>(null);

  // Prediction form state
  const [predAssetId, setPredAssetId] = useState("");
  const [predSourceId, setPredSourceId] = useState("");
  const [predResult, setPredResult] = useState<PredictionJobResult | null>(null);

  // Anomaly form state
  const [anomAssetId, setAnomAssetId] = useState("");
  const [anomSourceId, setAnomSourceId] = useState("");
  const [zThreshold, setZThreshold] = useState(2.5);
  const [anomResult, setAnomResult] = useState<{
    total_anomalies: number;
    z_score_anomalies: number;
    bollinger_breaches: number;
    volume_spikes: number;
  } | null>(null);

  const {
    data: totalsData,
    error: totalsError,
    isLoading: totalsLoading,
    mutate: mutateTotals,
  } = useTotals();
  const {
    data: predsData,
    error: predsError,
    isLoading: predsLoading,
    mutate: mutatePreds,
  } = usePredictions();
  const {
    data: anomData,
    error: anomError,
    isLoading: anomLoading,
    mutate: mutateAnom,
  } = useAnomalies(anomAssetId || undefined);
  const { data: assetsData } = useAssets(0, 100);
  const { data: sourcesData } = useDataSources(0, 100);

  const assetOptions = (assetsData?.items || []).map((id) => ({
    value: id,
    label: id,
  }));
  const sourceOptions = (sourcesData?.items || []).map((id) => ({
    value: id,
    label: id,
  }));

  const handleRunAggregation = async () => {
    setRunning(true);
    setJobError(null);
    try {
      await api.runAggregation();
      await mutateTotals();
    } catch (e) {
      setJobError(
        e instanceof Error ? e.message : "Aggregation job failed",
      );
    }
    setRunning(false);
  };

  const handleRunPrediction = async () => {
    if (!predAssetId || !predSourceId) return;
    setRunning(true);
    setJobError(null);
    setPredResult(null);
    try {
      const result = await api.runPrediction(predAssetId, predSourceId);
      setPredResult(result);
      await mutatePreds();
    } catch (e) {
      setJobError(
        e instanceof Error ? e.message : "Prediction job failed",
      );
    }
    setRunning(false);
  };

  const handleRunAnomalyDetection = async () => {
    if (!anomAssetId || !anomSourceId) return;
    setRunning(true);
    setJobError(null);
    setAnomResult(null);
    try {
      const result = await api.runAnomalyDetection(anomAssetId, anomSourceId, zThreshold);
      setAnomResult(result);
      await mutateAnom();
    } catch (e) {
      setJobError(
        e instanceof Error ? e.message : "Anomaly detection job failed",
      );
    }
    setRunning(false);
  };

  const barData =
    totalsData?.totals?.map((t) => ({
      name: `${t.asset_id.split("/").pop()} (${t.business_date_year})`,
      value: t.count,
    })) ?? [];

  const predChartData =
    predsData?.predictions?.map((p) => ({
      date: String(p.seconds),
      value: p.predicted_open,
    })) ?? [];

  const totalsRows =
    totalsData?.totals?.map((t) => ({
      Asset: t.asset_id,
      Year: String(t.business_date_year),
      Count: String(t.count),
    })) ?? [];

  const predRows =
    predsData?.predictions?.map((p) => ({
      Seconds: String(p.seconds),
      "Actual Open": p.actual_open.toFixed(2),
      "Predicted Open": p.predicted_open.toFixed(2),
    })) ?? [];

  const anomalyRows =
    anomData?.anomalies?.map((a) => ({
      Date: a.business_date,
      Asset: a.asset_id,
      Close: a.close.toFixed(2),
      "Z-Score": a.z_score.toFixed(3),
      "Z-Flag": a.z_flag ? "Yes" : "--",
      "BB-Flag": a.bb_flag ? "Yes" : "--",
      "Vol-Flag": a.vol_flag ? "Yes" : "--",
    })) ?? [];

  const TABS = ["aggregation", "predictions", "anomalies"] as const;

  return (
    <div>
      <GradientHeader
        title="Analytics"
        subtitle="Run aggregation, ML prediction, and anomaly detection jobs on your data"
      />

      <div className="flex gap-2 mb-6" role="tablist" aria-label="Analytics tabs">
        {TABS.map((tab) => (
          <button
            key={tab}
            role="tab"
            aria-selected={activeTab === tab}
            onClick={() => setActiveTab(tab)}
            className={clsx(
              "px-6 py-2 rounded-full text-sm font-medium transition-all",
              activeTab === tab
                ? "bg-gradient-to-r from-accent-purple to-accent-pink text-white"
                : "glass text-[var(--text-secondary)] hover:text-white",
            )}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {running && <GlassLoader />}
      {jobError && (
        <div className="mb-6">
          <ErrorDisplay message={jobError} />
        </div>
      )}

      {/* ── Aggregation Tab ── */}
      {activeTab === "aggregation" && (
        <div role="tabpanel" aria-label="Aggregation panel">
          <div className="flex gap-4 mb-6">
            <button
              onClick={handleRunAggregation}
              disabled={running}
              className="gradient-btn text-sm disabled:opacity-50"
            >
              Run Aggregation Job
            </button>
          </div>

          {totalsLoading && <GlassLoader />}
          {totalsError && (
            <ErrorDisplay
              message={totalsError.message}
              onRetry={() => mutateTotals()}
            />
          )}

          {!totalsLoading && !totalsError && barData.length > 0 ? (
            <FadeIn>
              <GlassPanel className="mb-6">
                <h2 className="text-lg font-semibold text-white mb-4">
                  Record Counts by Asset & Year
                </h2>
                <AnimatedBarChart data={barData} height={350} />
              </GlassPanel>
              <GlassPanel>
                <AnimatedDataTable
                  columns={["Asset", "Year", "Count"]}
                  rows={totalsRows}
                />
              </GlassPanel>
            </FadeIn>
          ) : (
            !totalsLoading &&
            !totalsError && (
              <EmptyState
                title="No aggregation data"
                message="Run an aggregation job to see results."
              />
            )
          )}
        </div>
      )}

      {/* ── Predictions Tab ── */}
      {activeTab === "predictions" && (
        <div role="tabpanel" aria-label="Predictions panel">
          {/* Prediction trigger form */}
          <GlassPanel className="mb-6">
            <h3 className="text-sm font-semibold text-white mb-3">
              Run Prediction Job
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
              <GlassSelect
                label="Asset"
                value={predAssetId}
                onChange={setPredAssetId}
                options={assetOptions}
                placeholder="Select asset..."
              />
              <GlassSelect
                label="Data Source"
                value={predSourceId}
                onChange={setPredSourceId}
                options={sourceOptions}
                placeholder="Select source..."
              />
              <button
                onClick={handleRunPrediction}
                disabled={running || !predAssetId || !predSourceId}
                className="gradient-btn text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Run Prediction
              </button>
            </div>
          </GlassPanel>

          {/* Model metrics after prediction job */}
          {predResult && predResult.metrics && (
            <FadeIn>
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-[var(--text-secondary)] mb-1">
                  Best Model
                </h3>
                <p className="text-2xl font-bold gradient-text mb-4">
                  {predResult.model_name}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <GlassMetricCard
                    title="RMSE"
                    value={predResult.metrics.rmse.toFixed(4)}
                    glow="purple"
                    delay={0}
                  />
                  <GlassMetricCard
                    title="R2"
                    value={predResult.metrics.r2.toFixed(4)}
                    glow="green"
                    delay={0.1}
                  />
                  <GlassMetricCard
                    title="MAE"
                    value={predResult.metrics.mae.toFixed(4)}
                    glow="blue"
                    delay={0.2}
                  />
                </div>
              </div>

              {/* Model comparison table */}
              {predResult.all_models && predResult.all_models.length > 0 && (
                <GlassPanel className="mb-6">
                  <h3 className="text-sm font-semibold text-white mb-3">
                    Model Comparison
                  </h3>
                  <AnimatedDataTable
                    columns={["Model", "RMSE", "R2", "MAE"]}
                    rows={predResult.all_models.map((m) => ({
                      Model: m.name,
                      RMSE: m.rmse.toFixed(4),
                      R2: m.r2.toFixed(4),
                      MAE: m.mae.toFixed(4),
                    }))}
                  />
                </GlassPanel>
              )}
            </FadeIn>
          )}

          {predsLoading && <GlassLoader />}
          {predsError && (
            <ErrorDisplay
              message={predsError.message}
              onRetry={() => mutatePreds()}
            />
          )}

          {!predsLoading && !predsError && predChartData.length > 0 ? (
            <FadeIn>
              <GlassPanel className="mb-6">
                <h2 className="text-lg font-semibold text-white mb-4">
                  Predicted vs Actual Open Prices
                </h2>
                <GradientLineChart data={predChartData} height={350} />
              </GlassPanel>
              <GlassPanel>
                <AnimatedDataTable
                  columns={["Seconds", "Actual Open", "Predicted Open"]}
                  rows={predRows}
                />
              </GlassPanel>
            </FadeIn>
          ) : (
            !predsLoading &&
            !predsError &&
            !predResult && (
              <EmptyState
                title="No prediction data"
                message="Select an asset and data source above, then run a prediction job."
              />
            )
          )}
        </div>
      )}

      {/* ── Anomalies Tab ── */}
      {activeTab === "anomalies" && (
        <div role="tabpanel" aria-label="Anomalies panel">
          {/* Anomaly detection trigger form */}
          <GlassPanel className="mb-6">
            <h3 className="text-sm font-semibold text-white mb-3">
              Run Anomaly Detection
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
              <GlassSelect
                label="Asset"
                value={anomAssetId}
                onChange={setAnomAssetId}
                options={assetOptions}
                placeholder="Select asset..."
              />
              <GlassSelect
                label="Data Source"
                value={anomSourceId}
                onChange={setAnomSourceId}
                options={sourceOptions}
                placeholder="Select source..."
              />
              <div>
                <label className="block text-xs text-[var(--text-secondary)] mb-1">
                  Z-Score Threshold
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min={1}
                    max={5}
                    step={0.1}
                    value={zThreshold}
                    onChange={(e) => setZThreshold(parseFloat(e.target.value))}
                    className="flex-1 accent-[var(--accent-purple)]"
                  />
                  <GlassInput
                    value={String(zThreshold)}
                    onChange={(v) => {
                      const n = parseFloat(v);
                      if (!isNaN(n) && n >= 1 && n <= 5) setZThreshold(n);
                    }}
                    className="w-16 text-center"
                  />
                </div>
              </div>
              <button
                onClick={handleRunAnomalyDetection}
                disabled={running || !anomAssetId || !anomSourceId}
                className="gradient-btn text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Detect Anomalies
              </button>
            </div>
          </GlassPanel>

          {/* Summary metrics after anomaly detection */}
          {anomResult && (
            <FadeIn>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <GlassMetricCard
                  title="Total Anomalies"
                  value={anomResult.total_anomalies}
                  glow="pink"
                  delay={0}
                />
                <GlassMetricCard
                  title="Z-Score Anomalies"
                  value={anomResult.z_score_anomalies}
                  glow="purple"
                  delay={0.1}
                />
                <GlassMetricCard
                  title="Bollinger Breaches"
                  value={anomResult.bollinger_breaches}
                  glow="blue"
                  delay={0.2}
                />
                <GlassMetricCard
                  title="Volume Spikes"
                  value={anomResult.volume_spikes}
                  glow="green"
                  delay={0.3}
                />
              </div>
            </FadeIn>
          )}

          {/* Anomaly data table */}
          {anomLoading && <GlassLoader />}
          {anomError && (
            <ErrorDisplay
              message={anomError.message}
              onRetry={() => mutateAnom()}
            />
          )}

          {!anomLoading && !anomError && anomalyRows.length > 0 ? (
            <FadeIn>
              <GlassPanel>
                <h2 className="text-lg font-semibold text-white mb-4">
                  Detected Anomalies
                </h2>
                <AnimatedDataTable
                  columns={["Date", "Asset", "Close", "Z-Score", "Z-Flag", "BB-Flag", "Vol-Flag"]}
                  rows={anomalyRows}
                />
              </GlassPanel>
            </FadeIn>
          ) : (
            !anomLoading &&
            !anomError &&
            !anomResult && (
              <EmptyState
                title="No anomaly data"
                message="Select an asset and data source above, then run anomaly detection."
              />
            )
          )}
        </div>
      )}
    </div>
  );
}
