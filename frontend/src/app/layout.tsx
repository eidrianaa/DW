import type { Metadata } from "next";
import "@/styles/globals.css";
import { ResponsiveLayout } from "@/components/layout/ResponsiveLayout";

export const metadata: Metadata = {
  title: "Adri Financial Data Warehouse",
  description: "Acme Ltd Financial Data Warehouse - DDD + CQRS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[100]
                     focus:px-4 focus:py-2 focus:rounded-lg focus:bg-accent-purple focus:text-white
                     focus:outline-none"
        >
          Skip to content
        </a>
        <ResponsiveLayout>{children}</ResponsiveLayout>
      </body>
    </html>
  );
}
