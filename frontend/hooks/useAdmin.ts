"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchAdminLogs, fetchAdminStats } from "../lib/api";
import type { AdminLogItem, AdminStats } from "../types";

interface AdminState {
  stats: AdminStats | null;
  logs: AdminLogItem[];
  isLoading: boolean;
  error: string | null;
}

/**
 * Fetches admin dashboard stats and logs.
 */
export function useAdmin() {
  const [state, setState] = useState<AdminState>({
    stats: null,
    logs: [],
    isLoading: true,
    error: null,
  });

  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const [stats, logs] = await Promise.all([
        fetchAdminStats(),
        fetchAdminLogs(),
      ]);
      setState({ stats, logs, isLoading: false, error: null });
    } catch (error) {
      setState({
        stats: null,
        logs: [],
        isLoading: false,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { ...state, refresh };
}
