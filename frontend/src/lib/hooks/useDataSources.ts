import useSWR from "swr";
import { api } from "@/lib/api";

export function useDataSources(offset = 0, limit = 20) {
  return useSWR(
    [`/data-sources`, offset, limit],
    () => api.listDataSources(offset, limit),
    { revalidateOnFocus: false }
  );
}

export function useDataSourceDetails(sourceId: string | null) {
  return useSWR(
    sourceId ? [`/data-sources/${sourceId}`] : null,
    () => api.getDataSourceDetails(sourceId!),
    { revalidateOnFocus: false }
  );
}
