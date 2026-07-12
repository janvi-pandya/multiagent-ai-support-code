/**
 * services/api.ts
 * Centralised API client for the TechMart AI Support backend.
 */

import axios, { AxiosInstance, AxiosError } from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Axios instance ───────────────────────────────────────────────────────────
const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT from localStorage on every request
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Global error handler
api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ─── Types ────────────────────────────────────────────────────────────────────
export interface ChatResponse {
  response:   string;
  agents:     string[];
  intent:     string;
  session_id: string;
  message_id: string;
  timestamp:  string;
}

export interface HistoryItem {
  role:      "user" | "assistant";
  content:   string;
  agents:    string[];
  timestamp: string;
}

export interface AnalyticsSummary {
  total_conversations: number;
  agent_usage:         Record<string, number>;
  avg_response_ms:     number;
  satisfaction_score:  number;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: async (email: string, password: string, name: string) => {
    const { data } = await api.post("/api/auth/register", { email, password, name });
    localStorage.setItem("token", data.token);
    return data;
  },

  login: async (email: string, password: string) => {
    const { data } = await api.post("/api/auth/login", { email, password });
    localStorage.setItem("token", data.token);
    return data;
  },

  logout: () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  },

  isAuthenticated: () =>
    typeof window !== "undefined" && !!localStorage.getItem("token"),
};

// ─── Chat ─────────────────────────────────────────────────────────────────────
export const chatAPI = {
  sendMessage: async (message: string, sessionId?: string): Promise<ChatResponse> => {
    const { data } = await api.post("/api/chat/message", {
      message,
      session_id: sessionId,
    });
    return data;
  },

  getHistory: async (sessionId: string): Promise<HistoryItem[]> => {
    const { data } = await api.get(`/api/chat/history/${sessionId}`);
    return data.messages;
  },

  getSessions: async () => {
    const { data } = await api.get("/api/chat/sessions");
    return data.sessions;
  },
};

// ─── Analytics ────────────────────────────────────────────────────────────────
export const analyticsAPI = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    const { data } = await api.get("/api/analytics/summary");
    return data;
  },
};

export default api;
