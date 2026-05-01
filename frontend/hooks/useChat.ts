"use client";

import { useCallback, useMemo, useRef, useState } from "react";

import { ApiError, reportInteraction, sendChat } from "../lib/api";
import type { Message, SourceReference } from "../types";
import { useChatStore, type ChatState } from "../store/chatStore";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  language: string;
  sendMessage: (text: string) => Promise<void>;
  setLanguage: (lang: string) => void;
  clearChat: () => void;
  reportLast: () => Promise<void>;
}

const createSessionId = (): string => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const nanoid = (): string =>
  `msg-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const scrollToBottom = () => {
  if (typeof document === "undefined") {
    return;
  }
  const container = document.querySelector("[data-chat-window]");
  if (container instanceof HTMLElement) {
    container.scrollTop = container.scrollHeight;
  }
};

const showToast = (message: string, tone: "success" | "error") => {
  if (typeof document === "undefined") {
    return;
  }

  const toast = document.createElement("div");
  toast.textContent = message;
  toast.setAttribute("role", "status");
  toast.style.position = "fixed";
  toast.style.bottom = "24px";
  toast.style.right = "24px";
  toast.style.zIndex = "9999";
  toast.style.padding = "10px 14px";
  toast.style.borderRadius = "10px";
  toast.style.fontSize = "14px";
  toast.style.color = "#ffffff";
  toast.style.background = tone === "success" ? "#166534" : "#991b1b";
  toast.style.boxShadow = "0 12px 24px rgba(0, 0, 0, 0.2)";
  document.body.appendChild(toast);

  window.setTimeout(() => {
    toast.remove();
  }, 2500);
};

const createMessage = (
  overrides: Partial<Message> & {
    role: Message["role"];
    content: string;
  },
): Message => ({
  id: overrides.id ?? nanoid(),
  role: overrides.role,
  content: overrides.content,
  sources: overrides.sources ?? [],
  language: overrides.language ?? "en",
  wasRefused: overrides.wasRefused ?? false,
  timestamp: overrides.timestamp ?? new Date(),
  isLoading: overrides.isLoading,
});

/**
 * Manages chat state, history, and message sending.
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const language = useChatStore((state: ChatState) => state.language);
  const setLanguage = useChatStore((state: ChatState) => state.setLanguage);
  const sessionIdRef = useRef<string>(createSessionId());

  const lastUserMessage = useMemo(
    () => [...messages].reverse().find((message) => message.role === "user"),
    [messages],
  );
  const lastBotMessage = useMemo(
    () => [...messages].reverse().find((message) => message.role === "bot"),
    [messages],
  );

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) {
        setError("Please enter a message before sending.");
        return;
      }
      if (trimmed.length > 500) {
        setError("Message must be 500 characters or fewer.");
        return;
      }

      setError(null);
      const userMessage = createMessage({
        role: "user",
        content: trimmed,
        language,
        sources: [],
        wasRefused: false,
      });
      const loadingMessage = createMessage({
        role: "bot",
        content: "",
        language,
        sources: [],
        wasRefused: false,
        isLoading: true,
      });

      setMessages((prev: Message[]) => [...prev, userMessage, loadingMessage]);
      setIsLoading(true);

      try {
        const response = await sendChat({
          message: trimmed,
          session_id: sessionIdRef.current,
          language,
        });

        const botMessage = createMessage({
          role: "bot",
          content: response.reply,
          language: response.language,
          sources: response.sources as SourceReference[],
          wasRefused: response.was_refused,
        });

        setMessages((prev: Message[]) =>
          prev.map((message: Message) =>
            message.id === loadingMessage.id ? botMessage : message,
          ),
        );
        setError(null);
      } catch (caught) {
        if (caught instanceof ApiError && caught.status === 429) {
          const retryAfter = caught.retryAfter ?? 30;
          const notice = createMessage({
            role: "bot",
            content: `Service is busy. Please try again in ${retryAfter} seconds.`,
            language,
            sources: [],
            wasRefused: true,
          });
          setMessages((prev: Message[]) =>
            prev.map((message: Message) =>
              message.id === loadingMessage.id ? notice : message,
            ),
          );
        } else {
          const notice = createMessage({
            role: "bot",
            content: "Unable to reach the service. Check your connection.",
            language,
            sources: [],
            wasRefused: true,
          });
          setMessages((prev: Message[]) =>
            prev.map((message: Message) =>
              message.id === loadingMessage.id ? notice : message,
            ),
          );
          setError(caught instanceof Error ? caught.message : "Request failed");
        }
      } finally {
        setIsLoading(false);
        scrollToBottom();
      }
    },
    [language],
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const reportLast = useCallback(async () => {
    if (!lastBotMessage || !lastUserMessage) {
      showToast("No recent response to report.", "error");
      return;
    }

    try {
      await reportInteraction({
        session_id: sessionIdRef.current,
        query_preview: lastUserMessage.content.slice(0, 60),
      });
      showToast("Response reported. Our team will review it.", "success");
    } catch (caught) {
      showToast("Unable to report the response.", "error");
      setError(caught instanceof Error ? caught.message : "Report failed");
    }
  }, [lastBotMessage, lastUserMessage]);

  return {
    messages,
    isLoading,
    error,
    language,
    sendMessage,
    setLanguage,
    clearChat,
    reportLast,
  };
}
