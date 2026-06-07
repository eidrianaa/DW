import useSWR from "swr";
import { api } from "@/lib/api";

export function useAssets(offset = 0, limit = 20) {
  return useSWR(
    [`/assets`, offset, limit],
    () => api.listAssets(offset, limit),
    { revalidateOnFocus: false }
  );
}

export function useAssetDetails(assetId: string | null) {
  return useSWR(
    assetId ? [`/assets/${assetId}`] : null,
    () => api.getAssetDetails(assetId!),
    { revalidateOnFocus: false }
  );
}
