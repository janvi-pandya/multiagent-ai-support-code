/**
 * components/MessageBubble.tsx
 * Renders a single chat message with optional agent attribution badges.
 */

import React from "react";
import { Message } from "@/hooks/useChat";

const AGENT_META: Record<string, { icon: string; color: string; label: string }> = {
  billing:   { icon: "💳", color: "#818CF8", label: "Billing" },
  technical: { icon: "🔧", color: "#34D399", label: "Technical" },
  product:   { icon: "📦", color: "#60A5FA", label: "Product" },
  complaint: { icon: "🚨", color: "#F87171", label: "Complaint" },
  faq:       { icon: "❓", color: "#FBBF24", label: "FAQ" },
};

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  const renderContent = (text: string) => {
    // Render agent section headers (bolded __Agent Name__)
    return text.split("\n").map((line, i) => {
      if (line.startsWith("**") && line.endsWith("**")) {
        return (
          <div key={i} className="agent-section-header">
            {line.replace(/\*\*/g, "")}
          </div>
        );
      }
      return line ? (
        <span key={i}>
          {line}
          <br />
        </span>
      ) : (
        <br key={i} />
      );
    });
  };

  return (
    <div className={`message-row ${isUser ? "user-row" : "ai-row"}`}>
      {!isUser && (
        <div className="avatar" aria-label="AI assistant">
          AI
        </div>
      )}

      <div
        className={`bubble ${isUser ? "bubble-user" : "bubble-ai"} ${
          message.isError ? "bubble-error" : ""
        }`}
      >
        {/* Agent badges */}
        {!isUser && message.agents.length > 0 && (
          <div className="badge-row">
            {message.agents.map((key) => {
              const meta = AGENT_META[key];
              if (!meta) return null;
              return (
                <span
                  key={key}
                  className="agent-badge"
                  style={{ color: meta.color, borderColor: `${meta.color}55` }}
                >
                  {meta.icon} {meta.label}
                </span>
              );
            })}
          </div>
        )}

        {/* Message body */}
        <div className="bubble-text">{renderContent(message.content)}</div>

        {/* Timestamp */}
        <div className="bubble-time">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>
    </div>
  );
}
