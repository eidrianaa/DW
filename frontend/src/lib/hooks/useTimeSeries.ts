import useSWR from "swr";
import { api } from "@/lib/api";

export function useTimeSeries(
  assetId: string | null,
  dataSourceId: string | null,
  startDate: string | null,
  endDate: string | null,
  includeAttributes = false
) {
  const shouldFetch = assetId && dataSourceId && startDate && endDate;
  return useSWR(
    shouldFetch ? [`/data`, assetId, dataSourceId, startDate, endDate, includeAttributes] : null,
    () => api.getTimeSeries(assetId!, dataSourceId!, startDate!, endDate!, includeAttributes),
    { revalidateOnFocus: false }
  );
}
