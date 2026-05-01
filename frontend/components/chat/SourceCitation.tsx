"use client";

import { useState } from "react";
import type { SourceCitation as SourceCitationType } from "../../types";

interface SourceCitationProps {
  source: SourceCitationType;
}

/**
 * Collapsible source citation chip.
 */
export default function SourceCitation({ source }: SourceCitationProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <button
      type="button"
      onClick={() => setIsOpen((value) => !value)}
      style={{
        border: "1px solid #e5e7eb",
        background: "#f8fafc",
        borderRadius: 999,
        padding: "6px 10px",
        fontSize: 12,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        gap: 8,
      }}
    >
      <span style={{ fontWeight: 600 }}>{source.source_doc}</span>
      <span style={{ color: "#6b7280" }}>p.{source.page}</span>
      {isOpen ? (
        <div style={{ marginLeft: 8, color: "#6b7280", maxWidth: 320 }}>
          {source.section}
        </div>
      ) : null}
    </button>
  );
}
