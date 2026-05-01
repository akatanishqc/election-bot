"use client";

import { useState } from "react";
import { BOT_MODE_LABELS } from "../../lib/constants";
import { setBotMode } from "../../lib/api";
import type { BotMode } from "../../types";
import ConfirmModal from "./ConfirmModal";

interface BotModeToggleProps {
  currentMode: BotMode;
  onChanged: (mode: BotMode) => void;
}

/**
 * Kill switch UI to update bot mode.
 */
export default function BotModeToggle({
  currentMode,
  onChanged,
}: BotModeToggleProps) {
  const [pendingMode, setPendingMode] = useState<BotMode | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const modes: BotMode[] = ["ACTIVE", "RESTRICTED", "PAUSED"];

  const handleConfirm = async () => {
    if (!pendingMode) {
      return;
    }

    setIsSaving(true);
    try {
      const response = await setBotMode({ mode: pendingMode });
      onChanged(response.mode);
    } finally {
      setIsSaving(false);
      setPendingMode(null);
    }
  };

  return (
    <div>
      <div style={{ display: "flex", gap: 12 }}>
        {modes.map((mode) => (
          <button
            key={mode}
            type="button"
            onClick={() => setPendingMode(mode)}
            disabled={isSaving}
            style={{
              background: mode === currentMode ? "#1d4ed8" : "#e5e7eb",
              color: mode === currentMode ? "#ffffff" : "#111827",
              borderRadius: 999,
              padding: "6px 12px",
              border: "none",
              cursor: "pointer",
            }}
          >
            {BOT_MODE_LABELS[mode]}
          </button>
        ))}
      </div>
      {pendingMode ? (
        <ConfirmModal
          title="Confirm mode change"
          description={`Switch bot mode to ${BOT_MODE_LABELS[pendingMode]}?`}
          onConfirm={handleConfirm}
          onCancel={() => setPendingMode(null)}
        />
      ) : null}
    </div>
  );
}
