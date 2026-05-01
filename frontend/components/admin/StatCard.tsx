"use client";

interface StatCardProps {
  label: string;
  value: string | number;
}

/**
 * Admin stat summary card.
 */
export default function StatCard({ label, value }: StatCardProps) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: 12,
        padding: 16,
        minWidth: 180,
      }}
    >
      <div style={{ color: "#6b7280", fontSize: 12 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 600 }}>{value}</div>
    </div>
  );
}
