"use client";

import Link from "next/link";
import LanguagePicker from "../chat/LanguagePicker";

export default function Header() {
  return (
    <header className="header" aria-label="Site header">
      {/* Logo */}
      <Link
        href="/chat"
        className="logo-link"
        aria-label="ECI Election Information home"
      >
        <EciLogoMark />
        <div className="logo-text">
          <span className="logo-title">ECI Election Information</span>
          <span className="logo-sub">Official Electoral Procedures</span>
        </div>
      </Link>

      {/* Nav */}
      <nav className="nav" aria-label="Header navigation">
        <LanguagePicker />
        <Link href="/about" className="nav-link">
          About
        </Link>
      </nav>

      <style jsx>{`
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          height: 60px;
          gap: 12px;
        }
        .logo-link {
          display: flex;
          align-items: center;
          gap: 10px;
          text-decoration: none;
          color: inherit;
          flex-shrink: 0;
        }
        .logo-text {
          display: flex;
          flex-direction: column;
          line-height: 1.25;
        }
        .logo-title {
          font-weight: 700;
          font-size: 15px;
          color: var(--color-text);
          letter-spacing: -0.02em;
        }
        .logo-sub {
          font-size: 11px;
          color: var(--color-text-muted);
          font-weight: 400;
        }
        .nav {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .nav-link {
          font-size: 13px;
          font-weight: 500;
          color: var(--color-text-muted);
          text-decoration: none;
          padding: 4px 10px;
          border-radius: var(--radius-sm);
          transition:
            color 0.15s,
            background 0.15s;
          white-space: nowrap;
        }
        .nav-link:hover {
          color: var(--color-text);
          background: var(--color-border-light);
        }

        /* Mobile: hide subtitle */
        @media (max-width: 480px) {
          .logo-sub {
            display: none;
          }
          .logo-title {
            font-size: 14px;
          }
        }
      `}</style>
    </header>
  );
}

function EciLogoMark() {
  return (
    <svg
      width="34"
      height="34"
      viewBox="0 0 34 34"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      style={{ flexShrink: 0 }}
    >
      <rect width="34" height="34" rx="9" fill="#1642B4" />
      <rect x="7" y="9" width="20" height="4" rx="1.5" fill="#FF9933" />
      <rect x="7" y="15" width="20" height="4" rx="1.5" fill="#FFFFFF" />
      <rect x="7" y="21" width="20" height="4" rx="1.5" fill="#138808" />
      <circle cx="17" cy="17" r="2.5" fill="#00008B" opacity="0.85" />
    </svg>
  );
}
