"use client";
import clsx from "clsx";
import { motion } from "framer-motion";

interface ChatMessageProps {
  role: "user" | "assistant" | "error";
  content: string;
}

export function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === "user";
  const isError = role === "error";
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx("flex mb-3", isUser ? "justify-end" : "justify-start")}
    >
      <div
        className={clsx(
          "max-w-[80%] px-4 py-3 text-sm",
          isUser
            ? "glass-strong text-white rounded-2xl rounded-br-md"
            : isError
              ? "glass text-accent-red rounded-2xl rounded-bl-md border border-accent-red/30"
              : "glass text-white rounded-2xl rounded-bl-md"
        )}
      >
        <pre className="whitespace-pre-wrap font-sans">{content}</pre>
      </div>
    </motion.div>
  );
}
