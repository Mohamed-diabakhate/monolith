"use client";
import { useState } from "react";
import type { ChainKey, AddressBook } from "@/lib/types";
import { SUPPORTED_CHAINS } from "@/lib/chains";
import clsx from "clsx";

export function AddressForm({
  onSubmit,
}: {
  onSubmit: (payload: { addresses: AddressBook; chains: ChainKey[] }) => void;
}) {
  const [addresses, setAddresses] = useState<Partial<Record<ChainKey, string>>>(
    {}
  );
  const [selected, setSelected] = useState<ChainKey[]>([
    "eth-mainnet",
    "polygon-mainnet",
    "arbitrum-mainnet",
  ]);

  const update = (k: ChainKey, v: string) =>
    setAddresses((s) => ({ ...s, [k]: v }));
  const toggle = (k: ChainKey) =>
    setSelected((s) => (s.includes(k) ? s.filter((x) => x !== k) : [...s, k]));

  const submit = () => {
    const book: AddressBook = {};
    for (const k of Object.keys(addresses) as ChainKey[]) {
      const raw = addresses[k]?.trim();
      if (!raw) continue;
      const arr = raw
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean);
      if (arr.length) book[k] = arr;
    }
    onSubmit({ addresses: book, chains: selected });
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {SUPPORTED_CHAINS.map((c) => (
          <div key={c.key} className="rounded border p-3">
            <div className="flex items-center justify-between">
              <label className="font-medium">{c.label}</label>
              <button
                onClick={() => toggle(c.key)}
                className={clsx(
                  "px-2 py-1 text-sm rounded",
                  selected.includes(c.key)
                    ? "bg-green-600 text-white"
                    : "bg-gray-200"
                )}
              >
                {selected.includes(c.key) ? "Suivi" : "Ignoré"}
              </button>
            </div>
            <input
              placeholder="Adresse(s) séparées par des virgules"
              className="mt-2 w-full rounded border bg-transparent px-3 py-2"
              onChange={(e) => update(c.key, e.target.value)}
              value={addresses[c.key] ?? ""}
            />
          </div>
        ))}
      </div>
      <button
        onClick={submit}
        className="rounded bg-blue-600 px-4 py-2 font-semibold text-white"
      >
        Charger
      </button>
    </div>
  );
}
