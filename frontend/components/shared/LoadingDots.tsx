"use client";

/**
 * Three animated dots indicating bot is typing. Pure CSS animation, no JS.
 */
export default function LoadingDots() {
  return (
    <>
      <div className="loading-dots" aria-label="Loading response" role="status">
        <span />
        <span />
        <span />
      </div>
      <style jsx>{`
        .loading-dots {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 2px 0;
        }
        .loading-dots span {
          display: block;
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: var(--color-text-muted, #6b6560);
          animation: bounce 1.2s ease-in-out infinite;
        }
        .loading-dots span:nth-child(2) {
          animation-delay: 0.2s;
        }
        .loading-dots span:nth-child(3) {
          animation-delay: 0.4s;
        }
        @keyframes bounce {
          0%,
          80%,
          100% {
            transform: translateY(0);
            opacity: 0.4;
          }
          40% {
            transform: translateY(-6px);
            opacity: 1;
          }
        }
      `}</style>
    </>
  );
}
