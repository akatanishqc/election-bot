"use client";

import { useEffect, useRef } from "react";
import ChatWindow from "../../components/chat/ChatWindow";
import InputBar from "../../components/chat/InputBar";
import SuggestedQueries from "../../components/chat/SuggestedQueries";
import Footer from "../../components/shared/Footer";
import Header from "../../components/shared/Header";
import StatusBanner from "../../components/shared/StatusBanner";
import { useChat } from "../../hooks/useChat";

export default function ChatPage() {
  const { messages, isLoading, sendMessage } = useChat();
  const showSuggestions = messages.length === 0;

  useEffect(() => {
    document.title = "ECI Election Information | Chat";
  }, []);

  return (
    <>
      {/* Fixed header */}
      <div className="header-bar">
        <div className="container">
          <Header />
        </div>
      </div>

      {/* Status banner sits below header */}
      <div className="banner-slot">
        <StatusBanner />
      </div>

      {/* Main content area — fills space between header and input bar */}
      <main className="main">
        <div className="container chat-container">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            showEmptyState={showSuggestions}
            emptyState={<EmptyState onSelect={sendMessage} />}
          />
        </div>
      </main>

      {/* Fixed input bar */}
      <div className="input-bar-slot">
        <div className="container">
          <InputBar onSend={sendMessage} isLoading={isLoading} />
          <Footer />
        </div>
      </div>

      <style jsx>{`
        .header-bar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 30;
          background: rgba(245, 244, 240, 0.96);
          backdrop-filter: blur(12px);
          border-bottom: 1px solid var(--color-border);
        }
        .banner-slot {
          position: fixed;
          top: 60px;
          left: 0;
          right: 0;
          z-index: 29;
        }
        .container {
          width: 100%;
          max-width: 780px;
          margin: 0 auto;
          padding: 0 16px;
        }
        .main {
          /* 60px header + potential 44px banner accounted for via padding */
          padding-top: 76px;
          padding-bottom: 120px;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding-top: 16px;
          padding-bottom: 8px;
        }
        .input-bar-slot {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          z-index: 30;
          background: rgba(245, 244, 240, 0.97);
          backdrop-filter: blur(12px);
          border-top: 1px solid var(--color-border);
          padding: 12px 0 8px;
        }

        @media (max-width: 640px) {
          .main {
            padding-top: 72px;
            padding-bottom: 140px;
          }
        }
      `}</style>
    </>
  );
}

function EmptyState({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="empty">
      <div className="empty-icon" aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="12" fill="#EEF2FF" />
          <rect
            x="9"
            y="12"
            width="22"
            height="4"
            rx="2"
            fill="#1642B4"
            opacity="0.3"
          />
          <rect
            x="9"
            y="18"
            width="22"
            height="4"
            rx="2"
            fill="#1642B4"
            opacity="0.5"
          />
          <rect
            x="9"
            y="24"
            width="14"
            height="4"
            rx="2"
            fill="#1642B4"
            opacity="0.8"
          />
        </svg>
      </div>
      <h2 className="empty-title">Ask about Indian elections</h2>
      <p className="empty-desc">
        Get accurate answers sourced directly from official ECI documents.
      </p>
      <SuggestedQueries onSelect={onSelect} />

      <style jsx>{`
        .empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          gap: 12px;
          padding: 32px 16px;
          flex: 1;
        }
        .empty-icon {
          margin-bottom: 4px;
        }
        .empty-title {
          font-size: 20px;
          font-weight: 700;
          color: var(--color-text);
          letter-spacing: -0.02em;
        }
        .empty-desc {
          font-size: 14px;
          color: var(--color-text-muted);
          max-width: 320px;
          line-height: 1.5;
          margin-bottom: 8px;
        }
        @media (max-width: 480px) {
          .empty-title {
            font-size: 17px;
          }
          .empty {
            padding: 20px 8px;
          }
        }
      `}</style>
    </div>
  );
}
