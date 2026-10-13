import type { Metadata } from "next";
import "./styles/console.css";
import { NavLink } from "../components/NavLink.js";

export const metadata: Metadata = {
  title: "Caruca v2 · execution console",
  description: "v1 and v2 side by side, inside and out. Local only.",
};

/**
 * The shell: masthead, navigation, page.
 *
 * The masthead states the scope in plain sight - this page is local and makes no outside
 * requests. That is a property worth showing rather than documenting, because it is the reason
 * the console may display v1's man pages and specifications at all.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="masthead">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img className="masthead__logo" src="/logo.png" alt="Caruca" />
            <div className="masthead__titles">
              <div className="masthead__title">
                Caruca v2 <span>· execution console</span>
              </div>
              <div className="masthead__tagline">
                LLM-based specification mining for opaque shell commands.
              </div>
            </div>
            <div className="masthead__scope">127.0.0.1 · local only</div>
            {/*
              Four sections, in the order the work happens: run a command's pipeline, look at
              the runs it produced, compare the two sides across commands, read what was found.
              Live and Pre-flight are reached from a step on the Pipeline page, not from here.
            */}
            <nav className="nav" aria-label="Sections">
              <NavLink href="/">Pipeline</NavLink>
              <NavLink href="/runs">Runs</NavLink>
              <NavLink href="/compare">Compare</NavLink>
              <NavLink href="/findings">Findings</NavLink>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
