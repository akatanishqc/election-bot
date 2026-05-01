"use client";

interface ConfirmModalProps {
  title: string;
  description: string;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Simple confirmation modal.
 */
export default function ConfirmModal({
  title,
  description,
  onConfirm,
  onCancel,
}: ConfirmModalProps) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0, 0, 0, 0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 50,
      }}
    >
      <div
        style={{
          background: "#ffffff",
          padding: 20,
          borderRadius: 12,
          width: 320,
        }}
      >
        <h3 style={{ margin: 0 }}>{title}</h3>
        <p style={{ color: "#6b7280" }}>{description}</p>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            style={{ background: "#dc2626", color: "#ffffff" }}
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
