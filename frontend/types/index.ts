export type MessageRole = "user" | "bot";

export type BotMode = "ACTIVE" | "RESTRICTED" | "PAUSED";

export interface SourceReference {
  source_doc: string;
  section: string;
  page: number;
}

export type SourceCitation = SourceReference;

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  sources: SourceReference[];
  language: string;
  wasRefused: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

export type ChatMessage = Message;

export interface ChatRequest {
  message: string;
  session_id: string;
  language: string;
}

export interface ChatResponse {
  reply: string;
  sources: SourceCitation[];
  was_refused: boolean;
  language: string;
  session_id: string;
}

export interface StatusResponse {
  bot_mode: BotMode;
  message: string;
  silence_active: boolean;
  api_version: string;
}

export interface AdminStats {
  totalChats: number;
  activeUsers: number;
  lastUpdated: string;
}

export interface AdminLogItem {
  id: string;
  userMessage: string;
  botReply: string;
  createdAt: string;
  language?: string;
}

export interface ModeChangeRequest {
  mode: BotMode;
}

export interface ModeChangeResponse {
  mode: BotMode;
  updatedAt: string;
}
