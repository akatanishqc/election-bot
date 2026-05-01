"use client";

/**
 * Admin knowledge base status page.
 */
export default function AdminKnowledgePage() {
  return (
    <main>
      <h1>Knowledge Base</h1>
      <p>Ingestion pipeline is connected and waiting for documents.</p>
      <ul>
        <li>Last sync: not available</li>
        <li>Indexed documents: 0</li>
        <li>Vector index: ready</li>
      </ul>
    </main>
  );
}
