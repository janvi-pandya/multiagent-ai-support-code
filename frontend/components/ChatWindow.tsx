/**
 * components/ChatWindow.tsx
 * Main chat area: message feed + input bar.
 */

import React, { useRef, useEffect, useState, KeyboardEvent } from "react";
import { MessageBubble } from "./MessageBubble";
import { Message } from "@/hooks/useChat";

const SUGGESTIONS = [
  "My payment failed 3 times",
  "App crashes on startup",
  "Compare Pro vs Ultra",
  "I want a refund, this is unacceptable",
  "What are your business hours?",
  "I paid but Premium is still locked",
];

interface Props {
  messages:  Message[];
  isLoading: boolean;
  onSend:    (text: string) => void;
  onClear:   () => void;
}

export function ChatWindow({ messages, isLoading, onSend, onClear }: Props) {
  const [input, setInput]   = useState("");
  const feedRef             = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || isLoading) return;
    onSend(text);
    setInput("");
  };

  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) handleSend();
  };

  return (
    <div className="chat-window">
      {/* Header */}
      <header className="chat-header">
        <div>
          <h1 className="chat-title">Customer Support</h1>
          <p className="chat-subtitle">Multi-Agent AI · RAG-Powered · TechMart Electronics</p>
        </div>
        <div className="header-actions">
          <div className="online-badge">
            <span className="online-dot" />
            Live
          </div>
          <button className="clear-btn" onClick={onClear} title="Clear conversation">
            ↺
          </button>
        </div>
      </header>

      {/* Message feed */}
      <div className="message-feed" ref={feedRef}>
        {messages.length === 0 && (
          <div className="empty-state">
            <p className="empty-icon">🤖</p>
            <p className="empty-title">TechMart AI Support</p>
            <p className="empty-desc">
              Ask me anything about billing, technical issues, products, or company policies.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div className="message-row ai-row">
            <div className="avatar">AI</div>
            <div className="bubble bubble-ai">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <footer className="input-area">
        {/* Quick-reply chips */}
        <div className="suggestion-chips">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className="chip"
              onClick={() => setInput(s)}
              disabled={isLoading}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Text input */}
        <div className="input-row">
          <input
            className="message-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about billing, technical issues, products…"
            disabled={isLoading}
            aria-label="Chat message"
          />
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            aria-label="Send message"
          >
            {isLoading ? <span className="send-spinner" /> : "↑"}
          </button>
        </div>

        <p className="powered-by">
          Powered by Claude Multi-Agent Architecture · FAISS RAG · FastAPI
        </p>
      </footer>
    </div>
  );
}
