"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/", label: "Dashboard" },
  { href: "#portfolio", label: "Portfolio" },
  { href: "#aave", label: "Aave" },
  { href: "#settings", label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden md:block md:w-64 lg:w-72 shrink-0">
      <div className="sticky top-0 h-[100dvh] p-4">
        <div className="rounded-2xl bg-white/70 dark:bg-gray-900/60 shadow-sm ring-1 ring-black/5 backdrop-blur supports-[backdrop-filter]:bg-white/60 h-full p-6 flex flex-col gap-6">
          <div className="text-xl font-semibold tracking-tight">
            DeFi Dashboard
          </div>
          <nav className="flex-1 space-y-1">
            {nav.map((item) => {
              const active = item.href === "/" ? pathname === "/" : false;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    "block rounded-lg px-3 py-2 text-sm font-medium transition-colors " +
                    (active
                      ? "bg-indigo-600 text-white"
                      : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800")
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="text-xs text-gray-500">
            Inspired by{" "}
            <a
              className="underline"
              href="https://app.aave.com/"
              target="_blank"
              rel="noreferrer"
            >
              Aave
            </a>
          </div>
        </div>
      </div>
    </aside>
  );
}
