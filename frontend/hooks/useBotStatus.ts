"use client";

import { useEffect, useState } from "react";
import { fetchStatus } from "../lib/api";
import type { StatusResponse } from "../types";

/**
 * Polls /api/status every 30 seconds.
 * Used by StatusBanner to show/hide restricted or paused state.
 */
export function useBotStatus(): StatusResponse | null {
  const [status, setStatus] = useState<StatusResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await fetchStatus();
        if (!cancelled) setStatus(data);
      } catch {
        // silently ignore network errors
      }
    }

    poll();
    const id = setInterval(poll, 30_000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return status;
}
