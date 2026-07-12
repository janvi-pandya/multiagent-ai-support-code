/**
 * hooks/useChat.ts
 * Manages chat state, history, and multi-agent response flow.
 */

import { useState, useRef, useCallback, useEffect } from "react";
import { chatAPI, ChatResponse } from "@/services/api";

export interface Message {
  id:        string;
  role:      "user" | "assistant";
  content:   string;
  agents:    string[];
  intent?:   string;
  timestamp: Date;
  isError?:  boolean;
}

export interface AgentState {
  [key: string]: "idle" | "processing" | "done";
}

export function useChat(initialSessionId?: string) {
  const [messages,    setMessages]    = useState<Message[]>([]);
  const [sessionId,   setSessionId]   = useState<string | undefined>(initialSessionId);
  const [isLoading,   setIsLoading]   = useState(false);
  const [agentStates, setAgentStates] = useState<AgentState>({});
  const [routingLog,  setRoutingLog]  = useState<string[]>([]);
  const [error,       setError]       = useState<string | null>(null);

  const historyRef = useRef<{ role: string; content: string }[]>([]);

  // Load existing session on mount
  useEffect(() => {
    if (!initialSessionId) return;
    chatAPI.getHistory(initialSessionId).then((items) => {
      const loaded: Message[] = items.map((item, i) => ({
        id:        `history-${i}`,
        role:      item.role,
        content:   item.content,
        agents:    item.agents ?? [],
        timestamp: new Date(item.timestamp),
      }));
      setMessages(loaded);
      historyRef.current = items.map((m) => ({ role: m.role, content: m.content }));
    });
  }, [initialSessionId]);

  const simulateAgentActivity = useCallback((agents: string[]) => {
    // Mark all as processing
    const proc: AgentState = {};
    agents.forEach((a) => (proc[a] = "processing"));
    setAgentStates(proc);

    // Stagger "done" state for realistic feel
    agents.forEach((agent, i) => {
      setTimeout(() => {
        setAgentStates((prev) => ({ ...prev, [agent]: "done" }));
      }, 600 + i * 300);
    });

    // Reset after display
    setTimeout(() => setAgentStates({}), 4000 + agents.length * 300);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;

      setError(null);
      setRoutingLog([]);
      setIsLoading(true);

      // Optimistically add user message
      const userMsg: Message = {
        id:        `user-${Date.now()}`,
        role:      "user",
        content:   text.trim(),
        agents:    [],
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      historyRef.current.push({ role: "user", content: text.trim() });

      setRoutingLog(["🔍 Analysing intent..."]);

      try {
        const result: ChatResponse = await chatAPI.sendMessage(text, sessionId);

        // Update session ID
        if (!sessionId) setSessionId(result.session_id);

        setRoutingLog((prev) => [
          ...prev,
          `🎯 Intent: ${result.intent}`,
          `🔀 Routing → ${result.agents.join(", ")}`,
        ]);

        simulateAgentActivity(result.agents);

        await new Promise((r) => setTimeout(r, 300)); // brief pause before reply

        const aiMsg: Message = {
          id:        result.message_id,
          role:      "assistant",
          content:   result.response,
          agents:    result.agents,
          intent:    result.intent,
          timestamp: new Date(result.timestamp),
        };

        setMessages((prev) => [...prev, aiMsg]);
        historyRef.current.push({ role: "assistant", content: result.response });

        setRoutingLog((prev) => [...prev, "✅ Response delivered"]);
        setTimeout(() => setRoutingLog([]), 4000);
      } catch (err: any) {
        const errMsg = err?.response?.data?.detail ?? "Something went wrong. Please try again.";
        setError(errMsg);
        setMessages((prev) => [
          ...prev,
          {
            id:        `err-${Date.now()}`,
            role:      "assistant",
            content:   errMsg,
            agents:    [],
            timestamp: new Date(),
            isError:   true,
          },
        ]);
        setAgentStates({});
        setRoutingLog([]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, sessionId, simulateAgentActivity]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(undefined);
    historyRef.current = [];
    setAgentStates({});
    setRoutingLog([]);
    setError(null);
  }, []);

  return {
    messages,
    sessionId,
    isLoading,
    agentStates,
    routingLog,
    error,
    sendMessage,
    clearChat,
  };
}
