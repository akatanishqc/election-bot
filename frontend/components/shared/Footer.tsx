"use client";

import { useChat } from "../../hooks/useChat";

export default function Footer() {
  const { reportLast } = useChat();

  return (
    <footer className="footer" aria-label="Site footer">
      <p className="disclaimer">
        AI-generated from official ECI documents. Not official electoral advice.
      </p>
      <nav className="links" aria-label="Footer links">
        <a
          href="https://eci.gov.in"
          target="_blank"
          rel="noopener noreferrer"
          className="link"
        >
          eci.gov.in
        </a>
        <span className="sep" aria-hidden="true">
          ·
        </span>
        <a href="tel:1950" className="link">
          Helpline: 1950
        </a>
        <span className="sep" aria-hidden="true">
          ·
        </span>
        <button
          type="button"
          onClick={reportLast}
          className="report-btn"
          aria-label="Report the last bot response"
        >
          Report
        </button>
      </nav>

      <style jsx>{`
        .footer {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          justify-content: space-between;
          gap: 6px;
          padding: 6px 0 2px;
          font-size: 11.5px;
          color: var(--color-text-subtle);
          line-height: 1.5;
        }
        .disclaimer {
          margin: 0;
        }
        .links {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: wrap;
        }
        .link {
          color: var(--color-accent);
          text-decoration: none;
          font-weight: 500;
        }
        .link:hover {
          text-decoration: underline;
        }
        .sep {
          color: var(--color-border);
        }
        .report-btn {
          background: none;
          border: none;
          padding: 0;
          cursor: pointer;
          color: var(--color-text-subtle);
          font-size: 11.5px;
          font-family: inherit;
          text-decoration: underline;
          text-underline-offset: 2px;
        }
        .report-btn:hover {
          color: var(--color-text-muted);
        }

        @media (max-width: 480px) {
          .footer {
            justify-content: center;
            text-align: center;
          }
          .disclaimer {
            width: 100%;
          }
        }
      `}</style>
    </footer>
  );
}
