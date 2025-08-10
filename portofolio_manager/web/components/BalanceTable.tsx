"use client";
import type { TokenBalance } from "@/lib/types";

function fmt(n?: number) {
  if (n == null) return "-";
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export function BalanceTable({ tokens }: { tokens: TokenBalance[] }) {
  const filtered = tokens
    .filter((t) => (t.valueUsd ?? 0) > 1)
    .sort((a, b) => (b.valueUsd ?? 0) - (a.valueUsd ?? 0));
  return (
    <div className="overflow-x-auto rounded-2xl border bg-white/80 dark:bg-gray-900/70 shadow-sm ring-1 ring-black/5 backdrop-blur supports-[backdrop-filter]:bg-white/60 text-gray-900 dark:text-gray-100">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50/90 dark:bg-gray-800/80 text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs">
          <tr>
            <th className="px-4 py-2.5 text-left">Chain</th>
            <th className="px-4 py-2.5 text-left">Token</th>
            <th className="px-4 py-2.5 text-right">Price ($)</th>
            <th className="px-4 py-2.5 text-right">Value ($)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200/60 dark:divide-gray-800/60">
          {filtered.map((t, i) => (
            <tr
              key={i}
              className="odd:bg-white/40 even:bg-gray-50/40 dark:odd:bg-gray-900/40 dark:even:bg-gray-800/40"
            >
              <td className="px-4 py-2.5 font-medium">{t.chain}</td>
              <td className="px-4 py-2.5">{t.symbol}</td>
              <td className="px-4 py-2.5 text-right tabular-nums">
                {fmt(t.priceUsd)}
              </td>
              <td className="px-4 py-2.5 text-right font-semibold tabular-nums">
                {fmt(t.valueUsd)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
