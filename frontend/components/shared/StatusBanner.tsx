"use client";

import { useEffect, useState } from "react";
import { fetchStatus } from "../../lib/api";
import type { BotMode } from "../../types";

interface BannerState {
  mode: BotMode;
  message: string;
}

const BANNER_STYLES: Record<
  Exclude<BotMode, "ACTIVE">,
  { bg: string; border: string; color: string; icon: string }
> = {
  RESTRICTED: {
    bg: "#fffbeb",
    border: "#f59e0b",
    color: "#92400e",
    icon: "⚠",
  },
  PAUSED: {
    bg: "#fef2f2",
    border: "#ef4444",
    color: "#991b1b",
    icon: "✕",
  },
};

/**
 * Polls /api/status every 30s and shows a banner when bot is not ACTIVE.
 * Renders nothing when mode is ACTIVE.
 */
export default function StatusBanner() {
  const [banner, setBanner] = useState<BannerState | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const data = await fetchStatus();
        if (!cancelled && data.bot_mode !== "ACTIVE") {
          setBanner({ mode: data.bot_mode, message: data.message });
        } else if (!cancelled) {
          setBanner(null);
        }
      } catch {
        // silently ignore — don't break the UI if status endpoint is down
      }
    }

    poll();
    const interval = setInterval(poll, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  if (!banner || banner.mode === "ACTIVE") return null;

  const styles = BANNER_STYLES[banner.mode as Exclude<BotMode, "ACTIVE">];

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        background: styles.bg,
        borderTop: `3px solid ${styles.border}`,
        borderBottom: `1px solid ${styles.border}`,
        color: styles.color,
        padding: "10px 16px",
        display: "flex",
        alignItems: "center",
        gap: 8,
        fontSize: 13,
        fontWeight: 500,
      }}
    >
      <span aria-hidden="true" style={{ fontSize: 14 }}>
        {styles.icon}
      </span>
      <span>{banner.message}</span>
      <a
        href="https://eci.gov.in"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          marginLeft: "auto",
          color: styles.color,
          fontSize: 12,
          textDecoration: "underline",
          whiteSpace: "nowrap",
        }}
      >
        Visit eci.gov.in →
      </a>
    </div>
  );
}
