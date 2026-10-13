"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/**
 * A navigation link that knows when it is the current section.
 *
 * The shell is a server component and cannot read the path; this is the one client piece in
 * it. "/" is current only on the home page itself, so that "/runs/…" lights Runs, not Pipeline.
 */
export function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname() ?? "/";
  const current = href === "/" ? pathname === "/" : pathname.startsWith(href);
  return (
    <Link
      className={`nav__item${current ? " nav__item--active" : ""}`}
      href={href}
      aria-current={current ? "page" : undefined}
    >
      {children}
    </Link>
  );
}
