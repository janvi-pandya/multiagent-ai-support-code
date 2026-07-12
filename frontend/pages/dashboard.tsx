/**
 * pages/dashboard.tsx
 * Analytics dashboard – agent usage, response times, satisfaction.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import Link from "next/link";
import { analyticsAPI, AnalyticsSummary } from "@/services/api";
import { authAPI } from "@/services/api";

const AGENT_META: Record<string, { icon: string; color: string }> = {
  billing:   { icon: "💳", color: "#818CF8" },
  technical: { icon: "🔧", color: "#34D399" },
  product:   { icon: "📦", color: "#60A5FA" },
  complaint: { icon: "🚨", color: "#F87171" },
  faq:       { icon: "❓", color: "#FBBF24" },
};

// Simple bar chart using CSS widths
function BarChart({ data }: { data: Record<string, number> }) {
  const max = Math.max(...Object.values(data), 1);
  return (
    <div className="bar-chart">
      {Object.entries(data).map(([key, val]) => {
        const meta = AGENT_META[key] ?? { icon: "🔵", color: "#818CF8" };
        const pct  = Math.round((val / max) * 100);
        return (
          <div key={key} className="bar-row">
            <span className="bar-label">
              {meta.icon} {key.charAt(0).toUpperCase() + key.slice(1)}
            </span>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ width: `${pct}%`, background: meta.color }}
              />
            </div>
            <span className="bar-val">{val}</span>
          </div>
        );
      })}
    </div>
  );
}

export default function Dashboard() {
  const router = useRouter();
  const [data, setData]       = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authAPI.isAuthenticated()) { router.push("/login"); return; }
    analyticsAPI.getSummary()
      .then(setData)
      .finally(() => setLoading(false));
  }, [router]);

  // Mock data for demo while API loads
  const mockData: AnalyticsSummary = {
    total_conversations: data?.total_conversations ?? 248,
    agent_usage:         data?.agent_usage ?? {
      billing: 67, technical: 91, product: 54, complaint: 23, faq: 41,
    },
    avg_response_ms:     data?.avg_response_ms ?? 1240,
    satisfaction_score:  data?.satisfaction_score ?? 4.3,
  };

  const statCards = [
    { label: "Total Conversations", value: mockData.total_conversations, icon: "💬", color: "#818CF8" },
    { label: "Avg Response Time",   value: `${(mockData.avg_response_ms / 1000).toFixed(1)}s`, icon: "⚡", color: "#34D399" },
    { label: "Satisfaction Score",  value: `${mockData.satisfaction_score}/5`, icon: "⭐", color: "#FBBF24" },
    { label: "Active Agents",       value: Object.keys(AGENT_META).length,    icon: "🤖", color: "#60A5FA" },
  ];

  return (
    <>
      <Head><title>TechMart – Analytics Dashboard</title></Head>

      <div className="dash-layout">
        {/* Sidebar nav */}
        <nav className="dash-nav">
          <div className="brand">
            <div className="brand-mark">T</div>
            <div>
              <p className="brand-name">TechMart</p>
              <p className="brand-tag">Admin</p>
            </div>
          </div>
          <Link href="/"         className="nav-link">💬 Chat</Link>
          <Link href="/dashboard" className="nav-link nav-link-active">📊 Analytics</Link>
          <button
            className="nav-link nav-logout"
            onClick={() => authAPI.logout()}
          >
            🚪 Logout
          </button>
        </nav>

        {/* Main content */}
        <main className="dash-main">
          <h1 className="dash-title">Analytics Dashboard</h1>
          <p className="dash-sub">Real-time overview of agent performance and usage.</p>

          {/* Stat cards */}
          <div className="stat-grid">
            {statCards.map(({ label, value, icon, color }) => (
              <div key={label} className="stat-card" style={{ borderTopColor: color }}>
                <span className="stat-icon">{icon}</span>
                <p className="stat-val" style={{ color }}>{value}</p>
                <p className="stat-label">{label}</p>
              </div>
            ))}
          </div>

          {/* Agent usage chart */}
          <div className="dash-card">
            <h2 className="dash-card-title">Agent Usage Distribution</h2>
            <BarChart data={mockData.agent_usage} />
          </div>

          {/* Recent activity table */}
          <div className="dash-card">
            <h2 className="dash-card-title">Recent Conversations</h2>
            <table className="dash-table">
              <thead>
                <tr>
                  <th>Session ID</th>
                  <th>Intent</th>
                  <th>Agents Used</th>
                  <th>Status</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { id: "sess_a1b2", intent: "Payment failure", agents: ["billing"], status: "Resolved", time: "2m ago" },
                  { id: "sess_c3d4", intent: "App crash on macOS", agents: ["technical"], status: "Resolved", time: "7m ago" },
                  { id: "sess_e5f6", intent: "Compare products + billing", agents: ["product","billing"], status: "Resolved", time: "15m ago" },
                  { id: "sess_g7h8", intent: "Refund request", agents: ["complaint","billing"], status: "Escalated", time: "23m ago" },
                  { id: "sess_i9j0", intent: "Warranty question", agents: ["faq"], status: "Resolved", time: "31m ago" },
                ].map((row) => (
                  <tr key={row.id}>
                    <td className="mono">{row.id}</td>
                    <td>{row.intent}</td>
                    <td>
                      {row.agents.map((a) => (
                        <span
                          key={a}
                          className="agent-chip"
                          style={{ color: AGENT_META[a]?.color, borderColor: `${AGENT_META[a]?.color}44` }}
                        >
                          {AGENT_META[a]?.icon} {a}
                        </span>
                      ))}
                    </td>
                    <td>
                      <span className={`status-chip ${row.status === "Escalated" ? "escalated" : "resolved"}`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="muted">{row.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </>
  );
}
