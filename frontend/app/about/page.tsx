import Link from "next/link";
import Footer from "../../components/shared/Footer";
import Header from "../../components/shared/Header";

/**
 * About page with official ECI references.
 */
export default function AboutPage() {
  return (
    <main style={{ paddingBottom: 40 }}>
      <Header />
      <section style={{ marginTop: 24 }}>
        <h1>About Election Bot</h1>
        <p>
          Election Bot summarizes public information to help voters understand
          schedules, voting procedures, and official announcements.
        </p>
        <h2>Official sources</h2>
        <ul>
          <li>
            <Link href="https://eci.gov.in" target="_blank">
              Election Commission of India
            </Link>
          </li>
          <li>
            <Link href="https://voters.eci.gov.in" target="_blank">
              National Voters Service Portal
            </Link>
          </li>
        </ul>
        <p>
          This tool is informational only. Always verify critical details with
          official ECI notices.
        </p>
      </section>
      <Footer />
    </main>
  );
}
