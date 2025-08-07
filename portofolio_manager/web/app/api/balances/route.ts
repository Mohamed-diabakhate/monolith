import { NextRequest, NextResponse } from "next/server";

type AnkrAsset = {
  balance: string;
  balanceRawInteger: string;
  balanceUsd?: string;
  blockchain: string;
  contractAddress?: string;
  holderAddress?: string;
  tokenDecimals: number;
  tokenName: string;
  tokenPrice?: string;
  tokenSymbol: string;
  tokenType?: string;
  thumbnail?: string;
};

type AnkrResp = {
  result: {
    assets: AnkrAsset[];
    nextPageToken?: string;
    totalBalanceUsd?: string;
  };
};

function ankrUrl() {
  const key = process.env.ANKR_API_KEY?.trim();
  return key
    ? `https://rpc.ankr.com/multichain/${key}`
    : "https://rpc.ankr.com/multichain";
}

async function ankrGetAccountBalance(params: {
  walletAddress: string;
  blockchain?: string[];
  onlyWhitelisted?: boolean;
  pageToken?: string;
}) {
  const body = {
    jsonrpc: "2.0",
    method: "ankr_getAccountBalance",
    params,
    id: 1,
  };
  const res = await fetch(ankrUrl(), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    next: { revalidate: 15 },
  });
  if (!res.ok) throw new Error(`ANKR ${res.status}`);
  return (await res.json()) as AnkrResp;
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const address = (searchParams.get("address") ?? "").trim().toLowerCase();
  const chains = (searchParams.get("chains") ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const mock = searchParams.get("mock") === "1";
  if (!address)
    return NextResponse.json({ error: "address requis" }, { status: 400 });

  try {
    if (mock) {
      const buf = await import("@/mocks/balances.mock.json");
      return NextResponse.json(buf.default ?? buf);
    }
    const data = await ankrGetAccountBalance({
      walletAddress: address,
      blockchain: chains.length ? chains : undefined,
      onlyWhitelisted: true,
    });
    return NextResponse.json(data?.result ?? {});
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
