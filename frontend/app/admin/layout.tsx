"use client";

import { useEffect, useState, type ReactNode } from "react";
import { setAdminToken } from "../../lib/api";

/**
 * Admin auth guard and layout wrapper.
 */
export default function AdminLayout({ children }: { children: ReactNode }) {
  const [token, setToken] = useState("");
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem("adminToken");
    if (saved) {
      setToken(saved);
    }
    setIsReady(true);
  }, []);

  if (!isReady) {
    return null;
  }

  if (!token) {
    return (
      <main style={{ padding: "40px 0" }}>
        <h1>Admin Access</h1>
        <p>Enter the admin token to continue.</p>
        <input
          value={token}
          onChange={(event) => setToken(event.target.value)}
          style={{
            border: "1px solid #e5e7eb",
            padding: "8px 10px",
            borderRadius: 8,
          }}
        />
        <button
          type="button"
          onClick={() => setAdminToken(token)}
          style={{ marginLeft: 8 }}
        >
          Save
        </button>
      </main>
    );
  }

  return <div style={{ padding: "24px 0" }}>{children}</div>;
}
