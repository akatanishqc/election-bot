"use client";

import { LANGUAGE_OPTIONS } from "../../lib/constants";
import { useChatStore } from "../../store/chatStore";

/**
 * Dropdown to override the reply language.
 */
export default function LanguagePicker() {
  const language = useChatStore((state) => state.language);
  const setLanguage = useChatStore((state) => state.setLanguage);

  return (
    <select
      value={language}
      onChange={(event) => setLanguage(event.target.value)}
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: 8,
        padding: "6px 8px",
      }}
    >
      {LANGUAGE_OPTIONS.map((option) => (
        <option key={option.code} value={option.code}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
