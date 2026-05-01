"use client";

import { useEffect, useRef, type ReactNode } from "react";
import type { ChatMessage } from "../../types";
import LoadingDots from "../shared/LoadingDots";
import MessageBubble from "./MessageBubble";

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
  emptyState?: ReactNode;
  showEmptyState?: boolean;
}

export default function ChatWindow({
  messages,
  isLoading,
  emptyState,
  showEmptyState = false,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div
      data-chat-window
      className="chat-window"
      role="log"
      aria-live="polite"
      aria-label="Chat messages"
    >
      {showEmptyState && messages.length === 0 ? (
        <div className="empty-wrapper">{emptyState}</div>
      ) : (
        <div className="messages">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="loading-row">
              <div className="loading-bubble">
                <LoadingDots />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      <style jsx>{`
        .chat-window {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
          border-radius: var(--radius-xl);
          border: 1px solid var(--color-border);
          background: var(--color-surface);
          box-shadow: var(--shadow-sm);
          min-height: 60vh;
        }
        .empty-wrapper {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .messages {
          display: flex;
          flex-direction: column;
          padding: 20px 16px;
          gap: 4px;
        }
        .loading-row {
          display: flex;
          justify-content: flex-start;
          margin-top: 8px;
        }
        .loading-bubble {
          background: var(--color-surface-2);
          border: 1px solid var(--color-border-light);
          border-radius: 6px 18px 18px 18px;
          padding: 12px 16px;
        }

        @media (max-width: 640px) {
          .chat-window {
            border-radius: var(--radius-lg);
            min-height: 55vh;
          }
          .messages {
            padding: 14px 10px;
          }
        }
      `}</style>
    </div>
  );
}
