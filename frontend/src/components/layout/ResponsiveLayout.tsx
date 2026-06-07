"use client";
import { useState } from "react";
import { GlassSidebar } from "./GlassSidebar";

/**
 * Wraps sidebar + main content.
 *  - On md+ the sidebar is always visible.
 *  - On mobile a hamburger button opens the sidebar as an overlay.
 *  - FloatingChatWidget removed from global layout (lives only on non-assistant pages via widget).
 */
export function ResponsiveLayout({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile hamburger button (visible < md) */}
      <button
        onClick={() => setMobileOpen(true)}
        aria-label="Open navigation menu"
        className="fixed top-4 left-4 z-[60] md:hidden w-10 h-10 rounded-xl glass
                   flex items-center justify-center hover:bg-white/10 transition-colors"
      >
        <svg
          className="w-5 h-5 text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      {/* Sidebar */}
      <GlassSidebar
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />

      {/* Main content */}
      <main
        id="main-content"
        className="min-h-screen p-8 pt-16 md:pt-8 md:ml-[72px]"
      >
        {children}
      </main>
    </>
  );
}
