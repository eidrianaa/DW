"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

const NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "/",
    icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  },
  {
    label: "Assets",
    href: "/assets",
    icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
  },
  {
    label: "Sources",
    href: "/data-sources",
    icon: "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4",
  },
  {
    label: "Explorer",
    href: "/explorer",
    icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
  },
  {
    label: "Ingestion",
    href: "/ingestion",
    icon: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
  },
  {
    label: "Assistant",
    href: "/assistant",
    icon: "M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z",
  },
];

interface GlassSidebarProps {
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function GlassSidebar({
  mobileOpen = false,
  onMobileClose,
}: GlassSidebarProps) {
  const [expanded, setExpanded] = useState(false);
  const pathname = usePathname();

  // Close mobile sidebar on route change
  useEffect(() => {
    onMobileClose?.();
  }, [pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  const sidebarContent = (
    <motion.aside
      animate={{ width: expanded ? 260 : 72 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className={clsx(
        "fixed left-0 top-0 h-full z-50 glass-strong flex flex-col items-center py-6",
        // On mobile, hide unless mobileOpen
        "hidden md:flex",
      )}
      style={{ borderRadius: "0 20px 20px 0" }}
      aria-label="Main navigation"
    >
      <div className="mb-8 flex items-center justify-center">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-purple to-accent-pink flex items-center justify-center">
          <span className="text-white font-bold text-lg">A</span>
        </div>
        {expanded && (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="ml-3 text-lg font-bold gradient-text whitespace-nowrap"
          >
            Adri DW
          </motion.span>
        )}
      </div>

      <nav className="flex-1 w-full px-3 space-y-2" aria-label="Sidebar">
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={clsx(
                  "flex items-center rounded-xl px-3 py-3 transition-all duration-200 group cursor-pointer",
                  isActive
                    ? "bg-gradient-to-r from-accent-purple/20 to-accent-pink/20 border-l-2 border-accent-purple glow-purple"
                    : "hover:bg-white/5",
                )}
              >
                <svg
                  className={clsx(
                    "w-6 h-6 flex-shrink-0",
                    isActive
                      ? "text-accent-purple"
                      : "text-gray-400 group-hover:text-white",
                  )}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d={item.icon}
                  />
                </svg>
                {expanded && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className={clsx(
                      "ml-3 text-sm font-medium whitespace-nowrap",
                      isActive
                        ? "text-white"
                        : "text-gray-400 group-hover:text-white",
                    )}
                  >
                    {item.label}
                  </motion.span>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      <button
        onClick={() => setExpanded(!expanded)}
        aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
        aria-expanded={expanded}
        className="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors"
      >
        <svg
          className={clsx(
            "w-5 h-5 text-gray-400 transition-transform",
            expanded && "rotate-180",
          )}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>
    </motion.aside>
  );

  return (
    <>
      {/* Desktop sidebar */}
      {sidebarContent}

      {/* Mobile overlay sidebar */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onMobileClose}
              className="fixed inset-0 bg-black/60 z-[70] md:hidden"
              aria-hidden="true"
            />
            {/* Sidebar */}
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="fixed left-0 top-0 h-full w-[260px] z-[80] glass-strong flex flex-col items-center py-6 md:hidden"
              style={{ borderRadius: "0 20px 20px 0" }}
              aria-label="Mobile navigation"
            >
              <div className="mb-8 flex items-center justify-center">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-purple to-accent-pink flex items-center justify-center">
                  <span className="text-white font-bold text-lg">A</span>
                </div>
                <span className="ml-3 text-lg font-bold gradient-text whitespace-nowrap">
                  Adri DW
                </span>
              </div>

              <nav
                className="flex-1 w-full px-3 space-y-2"
                aria-label="Mobile sidebar"
              >
                {NAV_ITEMS.map((item) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href !== "/" && pathname.startsWith(item.href));
                  return (
                    <Link key={item.href} href={item.href}>
                      <div
                        className={clsx(
                          "flex items-center rounded-xl px-3 py-3 transition-all duration-200 group cursor-pointer",
                          isActive
                            ? "bg-gradient-to-r from-accent-purple/20 to-accent-pink/20 border-l-2 border-accent-purple glow-purple"
                            : "hover:bg-white/5",
                        )}
                      >
                        <svg
                          className={clsx(
                            "w-6 h-6 flex-shrink-0",
                            isActive
                              ? "text-accent-purple"
                              : "text-gray-400 group-hover:text-white",
                          )}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={1.5}
                          aria-hidden="true"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d={item.icon}
                          />
                        </svg>
                        <span
                          className={clsx(
                            "ml-3 text-sm font-medium whitespace-nowrap",
                            isActive
                              ? "text-white"
                              : "text-gray-400 group-hover:text-white",
                          )}
                        >
                          {item.label}
                        </span>
                      </div>
                    </Link>
                  );
                })}
              </nav>

              <button
                onClick={onMobileClose}
                aria-label="Close navigation menu"
                className="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors"
              >
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
