import useSWR from "swr";
import { api } from "@/lib/api";

export function useTotals() {
  const { data, error, isLoading, mutate } = useSWR(
    ["/analytics/totals"],
    () => api.getTotals(),
    { revalidateOnFocus: false },
  );
  return { data, error, isLoading, mutate };
}

export function usePredictions() {
  const { data, error, isLoading, mutate } = useSWR(
    ["/analytics/predictions"],
    () => api.getPredictions(),
    { revalidateOnFocus: false },
  );
  return { data, error, isLoading, mutate };
}

export function useAnomalies(assetId?: string) {
  return useSWR(
    ["/analytics/anomalies", assetId],
    () => api.getAnomalies(assetId),
    { revalidateOnFocus: false }
  );
}
