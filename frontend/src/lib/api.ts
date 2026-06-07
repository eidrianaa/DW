const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/** Structured API error with HTTP status code. */
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly detail?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Core fetch wrapper with:
 *  - AbortController timeout (default 10 s)
 *  - Structured ApiError on non-2xx
 */
async function apiFetch<T>(
  path: string,
  init?: RequestInit,
  timeoutMs = 10_000,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${BASE}${path}`, {
      ...init,
      signal: controller.signal,
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(
        body.detail || `API error: ${res.status}`,
        res.status,
        body,
      );
    }

    return res.json();
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if ((err as Error).name === "AbortError") {
      throw new ApiError("Request timed out", 0);
    }
    throw new ApiError((err as Error).message ?? "Network error", 0);
  } finally {
    clearTimeout(timer);
  }
}

// ─── API client ────────────────────────────────────────────────────────────────

export const api = {
  // Assets
  listAssets: (offset = 0, limit = 20) =>
    apiFetch<PaginatedResponse<string>>(
      `/assets?offset=${offset}&limit=${limit}`,
    ),

  getAssetDetails: (id: string) =>
    apiFetch<AssetVersion[]>(`/assets/${encodeURIComponent(id)}`),

  // Data Sources
  listDataSources: (offset = 0, limit = 20) =>
    apiFetch<PaginatedResponse<string>>(
      `/data-sources?offset=${offset}&limit=${limit}`,
    ),

  getDataSourceDetails: (id: string) =>
    apiFetch<DataSourceVersion[]>(
      `/data-sources/${encodeURIComponent(id)}`,
    ),

  // Time Series
  getTimeSeries: (
    assetId: string,
    dsId: string,
    start: string,
    end: string,
    attrs = false,
  ) =>
    apiFetch<TimeSeriesResponse>(
      `/data?assetId=${encodeURIComponent(assetId)}&dataSourceId=${encodeURIComponent(dsId)}&startBusinessDate=${start}&endBusinessDate=${end}&includeAttributes=${attrs}`,
    ),

  // Ingestion (supports optional start_date, end_date, period)
  triggerIngestion: (
    provider: string,
    codes: string[],
    options?: { start_date?: string; end_date?: string; period?: string },
  ) =>
    apiFetch<IngestionStats>("/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider,
        dataset_codes: codes,
        ...(options?.start_date && { start_date: options.start_date }),
        ...(options?.end_date && { end_date: options.end_date }),
        ...(options?.period && { period: options.period }),
      }),
    }),

  // Analytics
  runAggregation: () =>
    apiFetch<{ status: string; rows_aggregated: number }>(
      "/analytics/aggregate",
      { method: "POST" },
    ),

  runPrediction: (assetId: string, dsId: string) =>
    apiFetch<PredictionJobResult>(
      "/analytics/predict",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          asset_id: assetId,
          data_source_id: dsId,
        }),
      },
    ),

  getTotals: () => apiFetch<TotalsResponse>("/analytics/totals"),
  getPredictions: () =>
    apiFetch<PredictionsResponse>("/analytics/predictions"),

  // Anomaly Detection
  runAnomalyDetection: (assetId: string, dsId: string, zThreshold = 2.5) =>
    apiFetch<AnomalyDetectionResult>("/analytics/anomalies", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ asset_id: assetId, data_source_id: dsId, z_threshold: zThreshold }),
    }),

  getAnomalies: (assetId?: string) =>
    apiFetch<AnomaliesResponse>(
      `/analytics/anomalies${assetId ? `?asset_id=${encodeURIComponent(assetId)}` : ""}`
    ),
};

// ─── API response types ────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  offset: number;
  limit: number;
  total: number;
  has_next: boolean;
}

export interface AssetVersion {
  id: string;
  system_time: string;
  name: string;
  description: string;
  attributes: Record<string, string>;
}

export interface DataSourceVersion {
  id: string;
  system_time: string;
  name: string;
  description: string;
  attributes: string[];
}

export interface TimeSeriesRecord {
  businessDate: string;
  values: Record<string, number | string>;
}

export interface TimeSeriesResponse {
  data: {
    assetId: string;
    datasourceId: string;
    records: TimeSeriesRecord[];
  };
  attributes?: string[];
}

export interface IngestionStats {
  fetched: number;
  stored: number;
  skipped: number;
  errors: number;
}

export interface TotalRow {
  asset_id: string;
  business_date_year: number;
  count: number;
}

export interface TotalsResponse {
  totals: TotalRow[];
}

export interface PredictionRow {
  seconds: number;
  actual_open: number;
  predicted_open: number;
}

export interface PredictionsResponse {
  predictions: PredictionRow[];
}

export interface ModelMetrics {
  rmse: number;
  r2: number;
  mae: number;
}

export interface ModelComparison {
  name: string;
  rmse: number;
  r2: number;
  mae: number;
}

export interface PredictionJobResult {
  status: string;
  predictions_generated: number;
  model_name: string;
  metrics: ModelMetrics;
  all_models: ModelComparison[];
}

export interface AnomalyDetectionResult {
  status: string;
  total_anomalies: number;
  z_score_anomalies: number;
  bollinger_breaches: number;
  volume_spikes: number;
}

export interface AnomalyRow {
  business_date: string;
  asset_id: string;
  close: number;
  z_score: number;
  z_flag: boolean;
  bb_flag: boolean;
  vol_flag: boolean;
}

export interface AnomaliesResponse {
  anomalies: AnomalyRow[];
}
