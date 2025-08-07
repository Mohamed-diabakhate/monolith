"use client";
import { useEffect, useMemo, useState } from "react";
import { BtcAltChart } from "@/components/BtcAltChart";
import { BalanceTable } from "@/components/BalanceTable";
import { AavePositions } from "@/components/AavePositions";
import type { ChainKey, Portfolio } from "@/lib/types";
import { Card, CardBody, StatCard } from "@/components/ui";
import { CONFIG } from "@/lib/config";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [chains, setChains] = useState<ChainKey[]>([]);
  const [activeWalletIndex, setActiveWalletIndex] = useState<number>(0);
  const [demo, setDemo] = useState<boolean>(true);
  const primaryAddress = useMemo(
    () =>
      CONFIG.wallets[activeWalletIndex]?.address ??
      "0x200b0E0b2030c4F9fba3312C3C7505b9050aaFD6",
    [activeWalletIndex]
  );

  const load = async () => {
    const defaultChains: ChainKey[] = [
      "eth-mainnet",
      "polygon-mainnet",
      "arbitrum-mainnet",
      "optimism-mainnet",
      "avalanche-mainnet",
    ];
    setChains(defaultChains);
    setLoading(true);
    try {
      // ANKR accepte blockchain list côté serveur; on agrège côté UI dans un second temps
      const qs = new URLSearchParams({
        address: primaryAddress,
        chains: ["eth", "polygon", "arbitrum", "optimism", "avalanche"].join(
          ","
        ),
        ...(demo ? { mock: "1" } : {}),
      }).toString();
      const res = await fetch(`/api/balances?${qs}`);
      const data: {
        assets?: Array<{
          tokenDecimals?: number;
          balanceRawInteger?: string;
          balance?: string;
          tokenPrice?: string;
          balanceUsd?: string;
          blockchain: string;
          contractAddress?: string;
          tokenSymbol: string;
          tokenName: string;
        }>;
      } = await res.json();
      // adapter au format Portfolio minimal pour l'UI
      const tokens = (data?.assets ?? []).map((a) => {
        const decimals = Number(a.tokenDecimals ?? 18);
        const raw = String(a.balanceRawInteger ?? a.balance ?? "0");
        const qty = Number(raw) / 10 ** decimals;
        const priceUsd = a.tokenPrice ? Number(a.tokenPrice) : undefined;
        const valueUsd =
          priceUsd != null
            ? qty * priceUsd
            : a.balanceUsd
            ? Number(a.balanceUsd)
            : undefined;
        return {
          chain: (a.blockchain + "-mainnet") as ChainKey,
          contract_address: a.contractAddress,
          symbol: a.tokenSymbol,
          name: a.tokenName,
          decimals,
          balance: raw,
          priceUsd,
          valueUsd,
        };
      });
      const total = tokens.reduce((s: number, t) => s + (t.valueUsd ?? 0), 0);
      const portfolio: Portfolio = {
        totals: { valueUsd: total, btcValueUsd: 0, altValueUsd: total },
        tokens,
      };
      setPortfolio(portfolio);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load demo automatically on first render
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeWalletIndex, demo]);

  const btc = portfolio?.totals.btcValueUsd ?? 0;
  const alt = portfolio?.totals.altValueUsd ?? 0;
  const total = portfolio?.totals.valueUsd ?? 0;

  return (
    <main className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Crypto Portfolio</h1>
          <div className="mt-1 text-sm text-gray-500">
            Multi-chain balances and Aave positions
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                className="h-4 w-4"
                checked={demo}
                onChange={(e) => setDemo(e.target.checked)}
                aria-label="Demo mode"
              />
              Demo
            </label>
            <select
              className="rounded border px-2 py-1 text-sm"
              value={activeWalletIndex}
              onChange={(e) => setActiveWalletIndex(Number(e.target.value))}
            >
              {CONFIG.wallets.map((w, i) => (
                <option key={w.address} value={i}>
                  {w.label ?? `Wallet ${i + 1}`} — {w.address.slice(0, 6)}…
                </option>
              ))}
            </select>
            <code className="rounded bg-gray-100 px-2 py-1 text-xs">
              {primaryAddress}
            </code>
          </div>
          <button
            onClick={load}
            className="rounded bg-indigo-600 px-3 py-1.5 text-white text-sm shadow-sm hover:brightness-110"
          >
            Load demo data
          </button>
        </div>
      </div>

      {loading && (
        <Card>
          <CardBody>Loading…</CardBody>
        </Card>
      )}

      {portfolio && (
        <>
          <section id="portfolio" className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <StatCard
                title="Total Value"
                value={`$${total.toLocaleString(undefined, {
                  maximumFractionDigits: 2,
                })}`}
              />
              <StatCard
                title="BTC"
                value={`$${btc.toLocaleString(undefined, {
                  maximumFractionDigits: 2,
                })}`}
                sub={`${((btc / (total || 1)) * 100).toFixed(1)}%`}
              />
              <StatCard
                title="Alts"
                value={`$${alt.toLocaleString(undefined, {
                  maximumFractionDigits: 2,
                })}`}
                sub={`${((alt / (total || 1)) * 100).toFixed(1)}%`}
              />
            </div>
            <Card>
              <CardBody className="p-4">
                <BtcAltChart btc={btc} alt={alt} />
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <BalanceTable tokens={portfolio.tokens} />
              </CardBody>
            </Card>
          </section>

          <section id="aave" className="space-y-4">
            <h2 className="text-lg font-semibold">Aave Positions</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {chains
                .filter((c) => ["arbitrum-mainnet"].includes(c))
                .map((c) => (
                  <Card key={c}>
                    <CardBody>
                      <AavePositions
                        address={primaryAddress}
                        chain={c}
                        mock={demo}
                      />
                    </CardBody>
                  </Card>
                ))}
              {/* Sonic (custom) */}
              <Card key="sonic-mainnet">
                <CardBody>
                  <AavePositions
                    address={primaryAddress}
                    chain={"sonic-mainnet" as unknown as ChainKey}
                    mock={demo}
                  />
                </CardBody>
              </Card>
            </div>
          </section>

          <section id="settings" className="space-y-4">
            <h2 className="text-lg font-semibold">Settings</h2>
            <Card>
              <CardBody>
                <div className="mb-3 text-sm text-gray-600">
                  Using wallets and contracts from configuration files.
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-3 py-2 text-left">Network</th>
                        <th className="px-3 py-2 text-left">Symbol</th>
                        <th className="px-3 py-2 text-left">Label</th>
                        <th className="px-3 py-2 text-left">Address</th>
                      </tr>
                    </thead>
                    <tbody>
                      {CONFIG.contracts.map((c, i) => (
                        <tr
                          key={`${c.address}-${i}`}
                          className="border-t border-gray-200"
                        >
                          <td className="px-3 py-2">{c.network}</td>
                          <td className="px-3 py-2">{c.symbol ?? "-"}</td>
                          <td className="px-3 py-2">{c.label ?? "-"}</td>
                          <td className="px-3 py-2">
                            <code className="text-xs">{c.address}</code>
                          </td>
                        </tr>
                      ))}
                      {!CONFIG.contracts.length && (
                        <tr>
                          <td
                            colSpan={4}
                            className="px-3 py-4 text-center text-gray-500"
                          >
                            No contracts configured
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </CardBody>
            </Card>
          </section>
        </>
      )}
    </main>
  );
}
