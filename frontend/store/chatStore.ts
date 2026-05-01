import { create } from "zustand";
import type { ChatMessage } from "../types";

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  language: string;
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  setLoading: (value: boolean) => void;
  setLanguage: (value: string) => void;
  resetChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  language: "auto",
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setMessages: (messages) => set({ messages }),
  setLoading: (value) => set({ isLoading: value }),
  setLanguage: (value) => set({ language: value }),
  resetChat: () => set({ messages: [], isLoading: false }),
}));
