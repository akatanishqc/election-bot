"use client";

interface SuggestedQueriesProps {
  onSelect: (query: string) => void;
  language?: string;
}

const SUGGESTIONS = [
  { icon: "🗳️", text: "How do I check if I'm registered to vote?" },
  { icon: "📍", text: "Where is my polling booth located?" },
  { icon: "🪪", text: "What documents do I need on election day?" },
  { icon: "📋", text: "How do I apply for a new Voter ID card?" },
  { icon: "📄", text: "What is Form 6 and how do I fill it?" },
  { icon: "🚨", text: "How do I report an election code violation?" },
];

export default function SuggestedQueries({ onSelect }: SuggestedQueriesProps) {
  return (
    <div className="grid">
      {SUGGESTIONS.map((s) => (
        <button
          key={s.text}
          type="button"
          onClick={() => onSelect(s.text)}
          className="chip"
          aria-label={s.text}
        >
          <span className="chip-icon" aria-hidden="true">
            {s.icon}
          </span>
          <span className="chip-text">{s.text}</span>
        </button>
      ))}

      <style jsx>{`
        .grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          width: 100%;
          max-width: 560px;
        }
        .chip {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          background: var(--color-surface);
          border: 1.5px solid var(--color-border);
          border-radius: var(--radius-md);
          padding: 10px 12px;
          cursor: pointer;
          text-align: left;
          font-family: inherit;
          font-size: 13px;
          color: var(--color-text);
          line-height: 1.4;
          transition:
            border-color 0.15s,
            background 0.15s,
            box-shadow 0.15s;
        }
        .chip:hover {
          border-color: var(--color-accent);
          background: var(--color-accent-light);
          box-shadow: 0 0 0 3px rgba(22, 66, 180, 0.08);
        }
        .chip-icon {
          font-size: 15px;
          flex-shrink: 0;
          margin-top: 1px;
        }
        .chip-text {
          flex: 1;
        }

        @media (max-width: 480px) {
          .grid {
            grid-template-columns: 1fr;
            max-width: 100%;
          }
          .chip {
            font-size: 13px;
            padding: 9px 11px;
          }
        }
      `}</style>
    </div>
  );
}
