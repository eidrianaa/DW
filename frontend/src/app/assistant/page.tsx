"use client";
import { GradientHeader } from "@/components/layout/GradientHeader";
import { ChatPanel } from "@/components/chat/ChatPanel";

export default function AssistantPage() {
  return (
    <div>
      <GradientHeader title="AI Assistant" subtitle="Chat with the data warehouse using natural language" />
      <ChatPanel fullPage />
    </div>
  );
}
