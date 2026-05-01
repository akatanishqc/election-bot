import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "ECI Election Information",
  description: "Official election process information for Indian voters.",
  openGraph: {
    title: "ECI Election Information",
    description: "Official election process information for Indian voters.",
    images: ["/og-image.png"],
  },
};

/**
 * Root layout with shared metadata and container.
 */
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          rel="preload"
          as="style"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&display=swap"
        />
        <link
          rel="preload"
          as="style"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap"
        />
        <link
          rel="preload"
          as="style"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap"
        />
        <link
          rel="preload"
          as="style"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap"
        />
        <link
          rel="preload"
          as="style"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&display=swap"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap"
        />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap"
        />
      </head>
      <body className="min-h-screen bg-[var(--color-bg)] text-[var(--color-text)]">
        <Providers>
          <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
