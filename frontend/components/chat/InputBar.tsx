"use client";

import { useRef, useState } from "react";
import { Send } from "lucide-react";

interface InputBarProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

const MAX_CHARS = 500;
const WARN_AT = 400;

export default function InputBar({
  onSend,
  isLoading,
  disabled = false,
}: InputBarProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function resize() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 112)}px`; // max ~4 lines
  }

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setValue(e.target.value);
    requestAnimationFrame(resize);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || isLoading || disabled || trimmed.length > MAX_CHARS) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  const len = value.length;
  const overLimit = len > MAX_CHARS;
  const nearLimit = len >= WARN_AT;
  const canSend =
    !isLoading && !disabled && value.trim().length > 0 && !overLimit;

  return (
    <div className="bar">
      {disabled && (
        <div className="paused-notice" role="alert">
          Service is currently paused. Visit eci.gov.in for information.
        </div>
      )}

      <div className="input-row">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask about voter registration, polling booths, election procedures..."
          rows={1}
          maxLength={MAX_CHARS + 10}
          disabled={disabled}
          aria-label="Type your election question"
          className="textarea"
        />

        <div className="send-col">
          <button
            type="button"
            onClick={submit}
            disabled={!canSend}
            aria-label="Send message"
            className={`send-btn ${canSend ? "send-btn-active" : "send-btn-idle"}`}
          >
            <Send size={16} />
            <span className="send-label">Send</span>
          </button>
          {nearLimit && (
            <span className={`counter ${overLimit ? "counter-over" : ""}`}>
              {len}/{MAX_CHARS}
            </span>
          )}
        </div>
      </div>

      <style jsx>{`
        .bar {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .paused-notice {
          background: #fef2f2;
          border: 1px solid #fecaca;
          border-radius: var(--radius-md);
          padding: 8px 12px;
          font-size: 13px;
          color: var(--color-danger);
          text-align: center;
        }

        .input-row {
          display: flex;
          align-items: flex-end;
          gap: 10px;
          background: var(--color-surface);
          border: 1.5px solid var(--color-border);
          border-radius: var(--radius-lg);
          padding: 8px 8px 8px 14px;
          box-shadow: var(--shadow-sm);
          transition:
            border-color 0.15s,
            box-shadow 0.15s;
        }
        .input-row:focus-within {
          border-color: var(--color-accent);
          box-shadow: 0 0 0 3px rgba(22, 66, 180, 0.1);
        }

        .textarea {
          flex: 1;
          border: none;
          outline: none;
          resize: none;
          background: transparent;
          font-family: inherit;
          font-size: 14.5px;
          line-height: 1.5;
          color: var(--color-text);
          min-height: 24px;
          max-height: 112px;
          padding: 2px 0;
        }
        .textarea::placeholder {
          color: var(--color-text-subtle);
        }
        .textarea:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .send-col {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 4px;
          flex-shrink: 0;
        }

        .send-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          border: none;
          border-radius: var(--radius-md);
          padding: 8px 14px;
          font-size: 13.5px;
          font-weight: 600;
          cursor: pointer;
          transition:
            background 0.15s,
            transform 0.1s;
        }
        .send-btn:active {
          transform: scale(0.97);
        }
        .send-btn-active {
          background: var(--color-accent);
          color: #fff;
        }
        .send-btn-active:hover {
          background: var(--color-accent-hover);
        }
        .send-btn-idle {
          background: var(--color-border-light);
          color: var(--color-text-subtle);
          cursor: not-allowed;
        }

        .counter {
          font-size: 11px;
          color: var(--color-text-subtle);
        }
        .counter-over {
          color: var(--color-danger);
          font-weight: 600;
        }

        /* Mobile: hide "Send" label, keep icon */
        @media (max-width: 480px) {
          .send-label {
            display: none;
          }
          .send-btn {
            padding: 9px 11px;
          }
          .textarea {
            font-size: 14px;
          }
        }
      `}</style>
    </div>
  );
}
