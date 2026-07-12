/**
 * components/AgentPanel.tsx
 * Sidebar that visualises which agents are active and shows the routing log.
 */

import React from "react";
import { AgentState } from "@/hooks/useChat";

const AGENTS = [
  { key: "billing",   icon: "💳", name: "Billing Agent",   desc: "Payments, invoices, refunds",  color: "#818CF8" },
  { key: "technical", icon: "🔧", name: "Technical Agent", desc: "Bugs, errors, installation",   color: "#34D399" },
  { key: "product",   icon: "📦", name: "Product Agent",   desc: "Features, pricing, comparisons",color: "#60A5FA" },
  { key: "complaint", icon: "🚨", name: "Complaint Agent", desc: "Escalations, dissatisfaction", color: "#F87171" },
  { key: "faq",       icon: "❓", name: "FAQ Agent",       desc: "Policies, general questions",  color: "#FBBF24" },
];

interface Props {
  agentStates:  AgentState;
  routingLog:   string[];
  stats:        { messages: number; agentCalls: number };
}

export function AgentPanel({ agentStates, routingLog, stats }: Props) {
  return (
    <aside className="agent-panel">
      {/* Brand */}
      <div className="brand">
        <div className="brand-mark">T</div>
        <div>
          <p className="brand-name">TechMart</p>
          <p className="brand-tag">AI Support Suite</p>
        </div>
      </div>

      <hr className="divider" />

      <p className="section-label">AGENT NETWORK</p>

      {AGENTS.map(({ key, icon, name, desc, color }) => {
        const status = agentStates[key];
        return (
          <div
            key={key}
            className="agent-card"
            style={{
              borderColor:  status ? color : "transparent",
              background:   status ? `${color}18` : undefined,
              boxShadow:    status === "processing" ? `0 0 18px ${color}44` : undefined,
            }}
          >
            <span className="agent-icon">{icon}</span>
            <div className="agent-info">
              <p className="agent-name" style={{ color: status ? color : undefined }}>
                {name}
              </p>
              <p className="agent-desc">{desc}</p>
            </div>
            <div
              className="status-dot"
              style={{
                background:
                  status === "processing" ? "#FBBF24"
                  : status === "done"     ? "#34D399"
                  :                         "#1E293B",
                animation: status === "processing" ? "pulse 0.9s infinite" : undefined,
              }}
            />
          </div>
        );
      })}

      {/* Routing log */}
      {routingLog.length > 0 && (
        <div className="routing-log">
          <p className="section-label">ROUTING LOG</p>
          {routingLog.map((line, i) => (
            <p key={i} className="log-line">{line}</p>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="stats-row">
        <div className="stat-box">
          <p className="stat-val">{stats.messages}</p>
          <p className="stat-label">QUERIES</p>
        </div>
        <div className="stat-box">
          <p className="stat-val">{stats.agentCalls}</p>
          <p className="stat-label">AGENT CALLS</p>
        </div>
      </div>
    </aside>
  );
}
