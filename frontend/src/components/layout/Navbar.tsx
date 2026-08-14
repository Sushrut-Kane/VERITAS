import { useState } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { ArrowRight, Menu, ShieldCheck, X } from "lucide-react";
import { useUiStore } from "@/lib/store/uiStore";

const links = [
  { to: "/upload", label: "Upload" },
  { to: "/review", label: "Review" },
  { to: "/catalog", label: "Catalog" },
] as const;

export function Navbar() {
  const demoUser = useUiStore((s) => s.demoUser);
  const signOut = useUiStore((s) => s.signOut);
  const [open, setOpen] = useState(false);
  // Remember where the user was so sign-in can return them there.
  const here = useRouterState({
    select: (s) => s.location.pathname + s.location.searchStr,
  });
  const loginSearch = here.startsWith("/login") ? {} : { redirect: here };

  return (
    <header className="sticky top-0 z-40 border-b bg-surface/85 backdrop-blur">
      <nav className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4 sm:gap-8 sm:px-6">
        <Link to="/" className="flex items-center gap-2" onClick={() => setOpen(false)}>
          <ShieldCheck className="h-4 w-4 text-primary" aria-hidden />
          <span className="data-value text-sm font-semibold tracking-[0.22em]">VERITAS</span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="rounded-sm px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground [&.active]:bg-accent [&.active]:text-accent-foreground"
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="ml-auto hidden items-center gap-3 text-xs text-muted-foreground md:flex">
          {demoUser ? (
            <>
              <span className="data-value">{demoUser}</span>
              <button onClick={signOut} className="rounded-sm border px-2 py-1 hover:bg-accent">
                Sign out
              </button>
            </>
          ) : (
            <Link
              to="/login"
              search={loginSearch}
              preload="intent"
              viewTransition
              className="group inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-xs font-medium text-primary-foreground shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:shadow-primary/25 focus-visible:ring-2 focus-visible:ring-ring/40 active:translate-y-0"
            >
              Sign in
              <ArrowRight
                className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5"
                aria-hidden
              />
            </Link>
          )}
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={open ? "Close menu" : "Open menu"}
          className="ml-auto inline-flex h-11 w-11 items-center justify-center rounded-sm border text-foreground transition-colors hover:bg-accent md:hidden"
        >
          {open ? <X className="h-5 w-5" aria-hidden /> : <Menu className="h-5 w-5" aria-hidden />}

        </button>
      </nav>

      {open ? (
        <div className="border-t bg-surface md:hidden">
          <div className="mx-auto flex max-w-6xl flex-col px-4 py-2">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setOpen(false)}
                className="rounded-sm px-3 py-3 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground [&.active]:bg-accent [&.active]:text-accent-foreground"
              >
                {link.label}
              </Link>
            ))}
            <div className="mt-2 flex items-center justify-between gap-3 border-t pt-3 text-xs text-muted-foreground">
              {demoUser ? (
                <>
                  <span className="data-value truncate">{demoUser}</span>
                  <button
                    onClick={() => {
                      signOut();
                      setOpen(false);
                    }}
                    className="rounded-sm border px-3 py-2 hover:bg-accent"
                  >
                    Sign out
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  search={loginSearch}
                  preload="intent"
                  viewTransition
                  onClick={() => setOpen(false)}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:opacity-90"
                >
                  Sign in
                  <ArrowRight className="h-4 w-4" aria-hidden />
                </Link>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </header>
  );
}
