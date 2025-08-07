"use client";
import { useEffect, useState } from "react";

type Row = {
  reserve: {
    symbol: string;
    name: string;
    decimals: number;
    underlyingAsset: string;
  };
  scaledATokenBalance: string;
  currentTotalDebt: string;
  usageAsCollateralEnabledOnUser: boolean;
};

export function AavePositions({
  address,
  chain,
  mock = false,
}: {
  address: string;
  chain: string;
  mock?: boolean;
}) {
  const [rows, setRows] = useState<Row[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!address || !chain) return;
    const url = `/api/aave?address=${address}&chain=${chain}${
      mock ? "&mock=1" : ""
    }`;
    fetch(url)
      .then((r) => r.json())
      .then((d) => {
        if (d?.data?.userReserves) setRows(d.data.userReserves);
        else setRows([]);
      })
      .catch((e) => setErr(String(e)));
  }, [address, chain, mock]);

  return (
    <div className="rounded-2xl border bg-white/80 dark:bg-gray-900/70 shadow-sm ring-1 ring-black/5 p-4 text-gray-900 dark:text-gray-100">
      <div className="mb-2 font-semibold">Aave — {chain}</div>
      {err && <div className="text-sm text-red-500">{err}</div>}
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50/90 dark:bg-gray-800/80 text-gray-700 dark:text-gray-200 uppercase tracking-wide text-xs">
            <tr>
              <th className="px-4 py-2.5 text-left">Asset</th>
              <th className="px-4 py-2.5 text-right">aToken (scaled)</th>
              <th className="px-4 py-2.5 text-right">Debt (raw)</th>
              <th className="px-4 py-2.5 text-center">Collateral</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200/60 dark:divide-gray-800/60">
            {rows.map((r, i) => (
              <tr
                key={i}
                className="odd:bg-white/40 even:bg-gray-50/40 dark:odd:bg-gray-900/40 dark:even:bg-gray-800/40"
              >
                <td className="px-4 py-2.5 font-medium">{r.reserve.symbol}</td>
                <td className="px-4 py-2.5 text-right tabular-nums">
                  {r.scaledATokenBalance}
                </td>
                <td className="px-4 py-2.5 text-right tabular-nums">
                  {r.currentTotalDebt}
                </td>
                <td className="px-4 py-2.5 text-center">
                  {r.usageAsCollateralEnabledOnUser ? "Yes" : "No"}
                </td>
              </tr>
            ))}
            {!rows.length && (
              <tr>
                <td colSpan={4} className="px-4 py-4 text-center text-gray-500">
                  No positions detected
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
