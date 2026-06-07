"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { api, ApiError } from "@/lib/api";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface Message {
  id: string;
  role: "user" | "assistant" | "error";
  content: string;
}

/**
 * Interpret a user query by calling real backend endpoints.
 *  - asset-related queries   -> /api/v1/assets
 *  - source-related queries  -> /api/v1/data-sources
 *  - fallback                -> generic help text
 */
async function interpretQuery(content: string): Promise<string> {
  const lower = content.toLowerCase();

  try {
    // Asset queries
    if (
      lower.includes("asset") ||
      lower.includes("instrument") ||
      lower.includes("ticker") ||
      lower.includes("stock")
    ) {
      const data = await api.listAssets(0, 20);
      if (data.items.length === 0) {
        return "There are currently no assets in the warehouse. Try running an ingestion first via the Ingestion page.";
      }
      return `Found ${data.total} asset(s). Here are the first ${data.items.length}:\n\n${data.items.map((id) => `- ${id}`).join("\n")}\n\nUse the Assets page or Data Explorer to inspect individual assets.`;
    }

    // Data source queries
    if (
      lower.includes("source") ||
      lower.includes("provider") ||
      lower.includes("data source")
    ) {
      const data = await api.listDataSources(0, 20);
      if (data.items.length === 0) {
        return "No data sources registered yet. Sources are created automatically during ingestion.";
      }
      return `Found ${data.total} data source(s):\n\n${data.items.map((id) => `- ${id}`).join("\n")}`;
    }

    // Analytics / totals
    if (
      lower.includes("total") ||
      lower.includes("aggregat") ||
      lower.includes("analytic")
    ) {
      const data = await api.getTotals();
      if (!data.totals || data.totals.length === 0) {
        return "No aggregation results yet. Run an aggregation job from the Analytics page.";
      }
      const summary = data.totals
        .slice(0, 10)
        .map((t) => `- ${t.asset_id} (${t.business_date_year}): ${t.count} records`)
        .join("\n");
      return `Aggregation totals (showing up to 10):\n\n${summary}`;
    }

    // Help / fallback
    return [
      "I can help you explore the data warehouse. Try asking about:",
      "",
      "- **Assets** -- \"What assets are available?\"",
      "- **Data Sources** -- \"List data sources\"",
      "- **Analytics** -- \"Show aggregation totals\"",
      "",
      "For time-series exploration, use the Data Explorer page.",
      "For ingestion, visit the Ingestion page.",
    ].join("\n");
  } catch (err) {
    if (err instanceof ApiError) {
      return `API error (${err.status}): ${err.message}`;
    }
    return `Error processing your request: ${(err as Error).message}`;
  }
}

export function ChatPanel({ fullPage = false }: { fullPage?: boolean }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm the Adri Financial Data Warehouse assistant. I can help you explore assets, data sources, and analytics data. What would you like to know?",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async (content: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const reply = await interpretQuery(content);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: reply,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "error",
          content: `Something went wrong: ${(err as Error).message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div
      className={`glass-strong flex flex-col ${fullPage ? "h-[calc(100vh-140px)]" : "h-[500px] w-[380px]"}`}
    >
      <div className="p-4 border-b border-white/10">
        <h3 className="font-semibold gradient-text">AI Assistant</h3>
        <div className="mt-1 h-[2px] w-16 bg-gradient-to-r from-accent-purple to-accent-pink rounded-full" />
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} role={msg.role} content={msg.content} />
        ))}
        {loading && (
          <div className="flex justify-start mb-3">
            <div className="glass px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <div
                  className="w-2 h-2 bg-accent-purple rounded-full animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <div
                  className="w-2 h-2 bg-accent-purple rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="w-2 h-2 bg-accent-purple rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="p-4 border-t border-white/10">
        <ChatInput onSend={handleSend} disabled={loading} />
      </div>
    </div>
  );
}
