"use client";

import { useState } from "react";
import BotModeToggle from "../../components/admin/BotModeToggle";
import StatCard from "../../components/admin/StatCard";
import { useAdmin } from "../../hooks/useAdmin";
import { useBotStatus } from "../../hooks/useBotStatus";
import type { BotMode } from "../../types";

/**
 * Admin dashboard overview page.
 */
export default function AdminDashboardPage() {
  const { stats, isLoading, error } = useAdmin();
  const { status } = useBotStatus();
  const [mode, setMode] = useState<BotMode>(status?.mode ?? "ACTIVE");

  const currentMode = status?.mode ?? mode;

  return (
    <main>
      <h1>Admin Dashboard</h1>
      {error ? <p style={{ color: "#dc2626" }}>{error}</p> : null}
      <section style={{ display: "flex", gap: 16, margin: "16px 0" }}>
        <StatCard
          label="Total chats"
          value={stats?.totalChats ?? (isLoading ? "..." : 0)}
        />
        <StatCard
          label="Active users"
          value={stats?.activeUsers ?? (isLoading ? "..." : 0)}
        />
        <StatCard label="Last updated" value={stats?.lastUpdated ?? "-"} />
      </section>
      <section style={{ marginTop: 24 }}>
        <h2>Bot mode</h2>
        <BotModeToggle currentMode={currentMode} onChanged={setMode} />
      </section>
    </main>
  );
}
