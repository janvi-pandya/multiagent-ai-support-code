/**
 * pages/login.tsx
 * Authentication page – login + register tabs.
 */

import { useState, FormEvent } from "react";
import Head from "next/head";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const [tab,      setTab]      = useState<"login" | "register">("login");
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [name,     setName]     = useState("");

  const { login, register, loading, error, clearError } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    if (tab === "login") {
      await login(email, password);
    } else {
      await register(email, password, name);
    }
  };

  return (
    <>
      <Head>
        <title>TechMart AI Support – Sign In</title>
      </Head>

      <div className="auth-page">
        {/* Left panel */}
        <div className="auth-left">
          <div className="auth-brand">
            <div className="auth-brand-mark">T</div>
            <div>
              <p className="auth-brand-name">TechMart</p>
              <p className="auth-brand-tag">Electronics</p>
            </div>
          </div>

          <div className="auth-hero">
            <h1 className="auth-headline">
              AI-Powered<br />Customer Support
            </h1>
            <p className="auth-subline">
              Intelligent multi-agent assistance for every TechMart query.
            </p>
          </div>

          <div className="auth-features">
            {[
              { icon: "🤖", text: "5 Specialised AI Agents" },
              { icon: "📚", text: "RAG-Powered Knowledge Base" },
              { icon: "⚡", text: "Real-time Parallel Routing" },
            ].map(({ icon, text }) => (
              <div key={text} className="auth-feature">
                <span>{icon}</span>
                <p>{text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel – form */}
        <div className="auth-right">
          <div className="auth-card">
            {/* Tabs */}
            <div className="auth-tabs">
              {(["login", "register"] as const).map((t) => (
                <button
                  key={t}
                  className={`auth-tab ${tab === t ? "auth-tab-active" : ""}`}
                  onClick={() => { setTab(t); clearError(); }}
                >
                  {t === "login" ? "Sign In" : "Register"}
                </button>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              {tab === "register" && (
                <div className="field">
                  <label htmlFor="name">Full Name</label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Jane Doe"
                    required
                  />
                </div>
              )}

              <div className="field">
                <label htmlFor="email">Email Address</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="jane@example.com"
                  required
                  autoComplete="email"
                />
              </div>

              <div className="field">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={8}
                  autoComplete={tab === "login" ? "current-password" : "new-password"}
                />
              </div>

              {error && <p className="auth-error">{error}</p>}

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading
                  ? "Please wait…"
                  : tab === "login"
                  ? "Sign In"
                  : "Create Account"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
