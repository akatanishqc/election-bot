"use client";

import type { AdminLogItem } from "../../types";

interface LogTableProps {
  logs: AdminLogItem[];
}

/**
 * Displays interaction logs.
 */
export default function LogTable({ logs }: LogTableProps) {
  if (logs.length === 0) {
    return <div>No interactions logged yet.</div>;
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left" }}>
            <th style={{ borderBottom: "1px solid #e5e7eb", padding: 8 }}>
              Time
            </th>
            <th style={{ borderBottom: "1px solid #e5e7eb", padding: 8 }}>
              User
            </th>
            <th style={{ borderBottom: "1px solid #e5e7eb", padding: 8 }}>
              Reply
            </th>
            <th style={{ borderBottom: "1px solid #e5e7eb", padding: 8 }}>
              Language
            </th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td style={{ borderBottom: "1px solid #f3f4f6", padding: 8 }}>
                {new Date(log.createdAt).toLocaleString()}
              </td>
              <td style={{ borderBottom: "1px solid #f3f4f6", padding: 8 }}>
                {log.userMessage}
              </td>
              <td style={{ borderBottom: "1px solid #f3f4f6", padding: 8 }}>
                {log.botReply}
              </td>
              <td style={{ borderBottom: "1px solid #f3f4f6", padding: 8 }}>
                {log.language ?? "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
