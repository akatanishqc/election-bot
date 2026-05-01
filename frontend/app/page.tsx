import { redirect } from "next/navigation";

/**
 * Redirects the landing page to the chat experience.
 */
export default function HomePage() {
  redirect("/chat");
}
