"use client";
import { useState } from "react";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { GlassPanel } from "@/components/layout/GlassPanel";
import { GlassInput } from "@/components/forms/GlassInput";
import { GlassSelect } from "@/components/forms/GlassSelect";
import { GlassDatePicker } from "@/components/forms/GlassDatePicker";
import { GlassMetricCard } from "@/components/cards/GlassMetricCard";
import { GlassLoader } from "@/components/common/GlassLoader";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { FadeIn } from "@/components/animations/FadeIn";
import { api, type IngestionStats } from "@/lib/api";

const PERIOD_OPTIONS = [
  { value: "", label: "No period (use dates)" },
  { value: "1mo", label: "1 Month" },
  { value: "3mo", label: "3 Months" },
  { value: "6mo", label: "6 Months" },
  { value: "1y", label: "1 Year" },
  { value: "2y", label: "2 Years" },
  { value: "5y", label: "5 Years" },
  { value: "max", label: "Max" },
];

export default function IngestionPage() {
  const [tickers, setTickers] = useState("");
  const [period, setPeriod] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IngestionStats | null>(null);

  const codes = tickers
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  const canSubmit = codes.length > 0 && !loading;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const options: {
        start_date?: string;
        end_date?: string;
        period?: string;
      } = {};
      if (period) options.period = period;
      if (startDate) options.start_date = startDate;
      if (endDate) options.end_date = endDate;

      const stats = await api.triggerIngestion(
        "NASDAQ-DATA-LINK",
        codes,
        Object.keys(options).length > 0 ? options : undefined,
      );
      setResult(stats);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Ingestion request failed",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <GradientHeader
        title="Data Ingestion"
        subtitle="Ingest financial time-series data from external providers"
      />

      <GlassPanel className="mb-8">
        <div className="space-y-6">
          {/* Ticker symbols */}
          <GlassInput
            label="Ticker Symbols (comma-separated)"
            placeholder="e.g. AAPL, MSFT, GOOGL"
            value={tickers}
            onChange={setTickers}
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Period selector */}
            <GlassSelect
              label="Period"
              value={period}
              onChange={setPeriod}
              options={PERIOD_OPTIONS}
            />

            {/* Optional date range */}
            <GlassDatePicker
              label="Start Date (optional)"
              value={startDate}
              onChange={setStartDate}
            />
            <GlassDatePicker
              label="End Date (optional)"
              value={endDate}
              onChange={setEndDate}
            />
          </div>

          {/* Parsed tickers preview */}
          {codes.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {codes.map((code) => (
                <span
                  key={code}
                  className="text-xs px-3 py-1 rounded-full bg-accent-purple/20 text-accent-purple border border-accent-purple/30"
                >
                  {code}
                </span>
              ))}
            </div>
          )}

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="w-full md:w-auto gradient-btn px-8 py-3 text-sm font-medium
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Start Ingestion
          </button>
        </div>
      </GlassPanel>

      {/* Loading */}
      {loading && (
        <div className="mb-6">
          <GlassLoader />
          <p className="text-center text-sm text-[var(--text-secondary)] mt-4">
            Ingesting data for {codes.length} ticker(s)... this may take a
            moment.
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-6">
          <ErrorDisplay message={error} onRetry={handleSubmit} />
        </div>
      )}

      {/* Results */}
      {result && (
        <FadeIn>
          <h2 className="text-lg font-semibold text-white mb-4">
            Ingestion Results
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassMetricCard
              title="Records Fetched"
              value={result.fetched}
              glow="blue"
              delay={0}
            />
            <GlassMetricCard
              title="Records Stored"
              value={result.stored}
              glow="green"
              delay={0.1}
            />
            <GlassMetricCard
              title="Records Skipped"
              value={result.skipped}
              glow="purple"
              delay={0.2}
            />
            <GlassMetricCard
              title="Errors"
              value={result.errors}
              glow={result.errors > 0 ? "pink" : "green"}
              delay={0.3}
            />
          </div>
        </FadeIn>
      )}
    </div>
  );
}
