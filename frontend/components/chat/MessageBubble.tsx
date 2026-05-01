"use client";

import { useState } from "react";
import type { Message } from "../../types";
import LoadingDots from "../shared/LoadingDots";
import SourceCitation from "./SourceCitation";

interface MessageBubbleProps {
  message: Message;
}

function formatTime(d: Date) {
  try {
    return new Date(d).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [expanded, setExpanded] = useState(false);
  const visibleSources = expanded
    ? message.sources
    : message.sources.slice(0, 3);

  return (
    <div className={`row ${isUser ? "row-user" : "row-bot"}`}>
      {/* Avatar dot for bot */}
      {!isUser && (
        <div className="avatar" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="#EEF2FF" />
            <rect
              x="6"
              y="8"
              width="16"
              height="3"
              rx="1"
              fill="#1642B4"
              opacity="0.4"
            />
            <rect
              x="6"
              y="13"
              width="16"
              height="3"
              rx="1"
              fill="#1642B4"
              opacity="0.6"
            />
            <rect
              x="6"
              y="18"
              width="10"
              height="3"
              rx="1"
              fill="#1642B4"
              opacity="0.9"
            />
          </svg>
        </div>
      )}

      <div
        className={`bubble ${isUser ? "bubble-user" : "bubble-bot"} ${message.wasRefused ? "bubble-refused" : ""}`}
      >
        {/* Content */}
        <div className="content">
          {message.isLoading ? (
            <LoadingDots />
          ) : (
            <p className="text">{message.content}</p>
          )}
        </div>

        {/* Sources */}
        {!message.isLoading && message.sources.length > 0 && (
          <div className="sources">
            {visibleSources.map((src) => (
              <SourceCitation
                key={`${src.source_doc}-${src.page}-${src.section}`}
                source={src}
              />
            ))}
            {message.sources.length > 3 && (
              <button
                type="button"
                className="more-btn"
                onClick={() => setExpanded((v) => !v)}
              >
                {expanded ? "Show less" : `+${message.sources.length - 3} more`}
              </button>
            )}
          </div>
        )}

        {/* Timestamp */}
        {message.timestamp && !message.isLoading && (
          <time className={`time ${isUser ? "time-user" : "time-bot"}`}>
            {formatTime(message.timestamp)}
          </time>
        )}
      </div>

      <style jsx>{`
        .row {
          display: flex;
          align-items: flex-end;
          gap: 8px;
          margin-bottom: 10px;
        }
        .row-user {
          justify-content: flex-end;
        }
        .row-bot {
          justify-content: flex-start;
        }

        .avatar {
          flex-shrink: 0;
          margin-bottom: 2px;
        }

        .bubble {
          max-width: 72%;
          padding: 10px 14px;
          line-height: 1.55;
          font-size: 14.5px;
          position: relative;
        }
        .bubble-user {
          background: var(--color-user-bubble);
          color: #fff;
          border-radius: 18px 18px 4px 18px;
          box-shadow: 0 2px 8px rgba(22, 66, 180, 0.25);
        }
        .bubble-bot {
          background: var(--color-surface);
          color: var(--color-text);
          border: 1px solid var(--color-border);
          border-radius: 4px 18px 18px 18px;
          box-shadow: var(--shadow-sm);
        }
        .bubble-refused {
          border-left: 3px solid #f59e0b;
        }

        .content {
          word-break: break-word;
        }
        .text {
          margin: 0;
          white-space: pre-wrap;
        }

        .sources {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
          margin-top: 10px;
          padding-top: 8px;
          border-top: 1px solid var(--color-border-light);
        }
        .more-btn {
          background: var(--color-surface-2);
          border: 1px solid var(--color-border);
          border-radius: 99px;
          padding: 3px 10px;
          font-size: 11px;
          cursor: pointer;
          color: var(--color-text-muted);
          transition: background 0.15s;
        }
        .more-btn:hover {
          background: var(--color-border-light);
        }

        .time {
          display: block;
          font-size: 10.5px;
          margin-top: 5px;
          opacity: 0.55;
        }
        .time-user {
          text-align: right;
          color: #fff;
        }
        .time-bot {
          text-align: left;
          color: var(--color-text-muted);
        }

        /* Mobile */
        @media (max-width: 480px) {
          .bubble {
            max-width: 88%;
            font-size: 14px;
            padding: 9px 12px;
          }
          .avatar {
            display: none;
          }
        }
      `}</style>
    </div>
  );
}
