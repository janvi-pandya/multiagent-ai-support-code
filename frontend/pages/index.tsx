/**
 * pages/index.tsx
 * Main chat page – requires authentication.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { ChatWindow }  from "@/components/ChatWindow";
import { AgentPanel }  from "@/components/AgentPanel";
import { useChat }     from "@/hooks/useChat";
import { authAPI }     from "@/services/api";

export default function Home() {
  const router = useRouter();
  const [agentCallCount, setAgentCallCount] = useState(0);

  useEffect(() => {
    if (!authAPI.isAuthenticated()) router.push("/login");
  }, [router]);

  const {
    messages,
    isLoading,
    agentStates,
    routingLog,
    sendMessage,
    clearChat,
  } = useChat();

  // Track total agent invocations for stats
  useEffect(() => {
    const last = messages[messages.length - 1];
    if (last?.role === "assistant" && last.agents.length > 0) {
      setAgentCallCount((c) => c + last.agents.length);
    }
  }, [messages]);

  const userMsgCount = messages.filter((m) => m.role === "user").length;

  return (
    <>
      <Head>
        <title>TechMart AI Support</title>
        <meta name="description" content="Multi-Agent AI Customer Support" />
      </Head>

      <main className="app-layout">
        <AgentPanel
          agentStates={agentStates}
          routingLog={routingLog}
          stats={{ messages: userMsgCount, agentCalls: agentCallCount }}
        />
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSend={sendMessage}
          onClear={clearChat}
        />
      </main>
    </>
  );
}
