export interface SourceCitation {
  title: string;
  url: string;
  snippet: string;
  relevance_score?: number;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: SourceCitation[];
}

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  reply: string;
  sources: SourceCitation[];
  metadata?: {
    model?: string;
    tokens_used?: number;
    response_time_ms?: number;
  };
}

export interface Conversation {
  id: string;
  messages: Message[];
}
