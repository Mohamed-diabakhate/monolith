"use client";
export function PortfolioSummary({
  total,
  btc,
  alt,
}: {
  total: number;
  btc: number;
  alt: number;
}) {
  const pct = (n: number, d: number) => (d ? (n / d) * 100 : 0);
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="rounded border p-4">
        <div className="text-sm text-gray-500">Total Value</div>
        <div className="text-2xl font-bold">
          ${total.toLocaleString(undefined, { maximumFractionDigits: 2 })}
        </div>
      </div>
      <div className="rounded border p-4">
        <div className="text-sm text-gray-500">BTC</div>
        <div className="text-xl font-semibold">
          ${btc.toLocaleString(undefined, { maximumFractionDigits: 2 })}
        </div>
        <div className="text-xs text-gray-500">
          {pct(btc, total).toFixed(1)}%
        </div>
      </div>
      <div className="rounded border p-4">
        <div className="text-sm text-gray-500">Altcoins</div>
        <div className="text-xl font-semibold">
          ${alt.toLocaleString(undefined, { maximumFractionDigits: 2 })}
        </div>
        <div className="text-xs text-gray-500">
          {pct(alt, total).toFixed(1)}%
        </div>
      </div>
    </div>
  );
}
