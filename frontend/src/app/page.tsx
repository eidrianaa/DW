"use client";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { GlassMetricCard } from "@/components/cards/GlassMetricCard";
import { GlassPanel } from "@/components/layout/GlassPanel";
import { GradientAreaChart } from "@/components/data/GradientAreaChart";
import { FadeIn } from "@/components/animations/FadeIn";
import { GlassLoader } from "@/components/common/GlassLoader";
import { ErrorDisplay } from "@/components/common/ErrorDisplay";
import { useAssets } from "@/lib/hooks/useAssets";
import { useDataSources } from "@/lib/hooks/useDataSources";

// Static demo chart data (no Math.random on every render)
const DEMO_CHART_DATA = [
  { date: "Jan", value: 620 },
  { date: "Feb", value: 710 },
  { date: "Mar", value: 680 },
  { date: "Apr", value: 890 },
  { date: "May", value: 820 },
  { date: "Jun", value: 950 },
  { date: "Jul", value: 1020 },
  { date: "Aug", value: 980 },
  { date: "Sep", value: 1100 },
  { date: "Oct", value: 1050 },
  { date: "Nov", value: 1180 },
  { date: "Dec", value: 1250 },
  { date: "Jan", value: 1200 },
  { date: "Feb", value: 1340 },
  { date: "Mar", value: 1280 },
  { date: "Apr", value: 1410 },
  { date: "May", value: 1350 },
  { date: "Jun", value: 1500 },
  { date: "Jul", value: 1460 },
  { date: "Aug", value: 1550 },
  { date: "Sep", value: 1620 },
  { date: "Oct", value: 1580 },
  { date: "Nov", value: 1700 },
  { date: "Dec", value: 1650 },
  { date: "Jan", value: 1780 },
  { date: "Feb", value: 1820 },
  { date: "Mar", value: 1750 },
  { date: "Apr", value: 1900 },
  { date: "May", value: 1870 },
  { date: "Jun", value: 1950 },
];

const SYSTEM_STATUS = [
  { name: "Cassandra", status: "Healthy", color: "bg-accent-green" },
  { name: "FastAPI Backend", status: "Running", color: "bg-accent-green" },
  { name: "Spark Cluster", status: "Standby", color: "bg-accent-blue" },
  { name: "MCP Server", status: "Available", color: "bg-accent-green" },
];

export default function DashboardPage() {
  const {
    data: assetsData,
    error: assetsError,
    isLoading: assetsLoading,
    mutate: mutateAssets,
  } = useAssets();
  const {
    data: sourcesData,
    error: sourcesError,
    isLoading: sourcesLoading,
    mutate: mutateSources,
  } = useDataSources();

  const isLoading = assetsLoading || sourcesLoading;
  const error = assetsError || sourcesError;

  return (
    <div>
      <GradientHeader
        title="Acme Financial Data Warehouse"
        subtitle="Real-time financial data analytics powered by DDD + CQRS"
      />

      {isLoading && (
        <div className="mb-6">
          <GlassLoader />
        </div>
      )}

      {error && (
        <div className="mb-6">
          <ErrorDisplay
            message={error.message}
            onRetry={() => {
              mutateAssets();
              mutateSources();
            }}
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <GlassMetricCard
          title="Total Assets"
          value={assetsData?.total ?? "--"}
          glow="purple"
          delay={0}
        />
        <GlassMetricCard
          title="Data Sources"
          value={sourcesData?.total ?? "--"}
          glow="pink"
          delay={0.1}
        />
        <GlassMetricCard
          title="Total Records"
          value="--"
          glow="blue"
          delay={0.2}
        />
        <GlassMetricCard
          title="Last Ingestion"
          value="--"
          glow="green"
          delay={0.3}
        />
      </div>

      <FadeIn delay={0.4}>
        <GlassPanel className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">
            Data Volume Over Time
          </h2>
          <GradientAreaChart data={DEMO_CHART_DATA} height={350} />
        </GlassPanel>
      </FadeIn>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FadeIn delay={0.5}>
          <GlassPanel>
            <h2 className="text-lg font-semibold text-white mb-4">
              Recent Activity
            </h2>
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <div className="w-12 h-12 mb-3 rounded-full bg-white/5 flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-gray-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <p className="text-sm text-[var(--text-secondary)]">
                No recent activity. Run an ingestion or analytics job to see
                events here.
              </p>
            </div>
          </GlassPanel>
        </FadeIn>

        <FadeIn delay={0.6}>
          <GlassPanel>
            <h2 className="text-lg font-semibold text-white mb-4">
              System Status{" "}
              <span className="text-xs font-normal text-[var(--text-secondary)]">
                (demo)
              </span>
            </h2>
            <div className="space-y-4">
              {SYSTEM_STATUS.map((service) => (
                <div
                  key={service.name}
                  className="flex items-center justify-between p-3 rounded-xl bg-white/5"
                >
                  <span className="text-sm text-white">{service.name}</span>
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${service.color}`}
                    />
                    <span className="text-xs text-[var(--text-secondary)]">
                      {service.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </GlassPanel>
        </FadeIn>
      </div>
    </div>
  );
}
