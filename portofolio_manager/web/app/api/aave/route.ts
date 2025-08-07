import { NextRequest, NextResponse } from "next/server";

const SUBGRAPHS: Record<string, string> = {
  "polygon-mainnet":
    "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-polygon",
  "arbitrum-mainnet":
    "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum",
  "optimism-mainnet":
    "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-optimism",
  "avalanche-mainnet":
    "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-avalanche",
};

const QUERY = `
query UserPositions($user: String!) {
  userReserves(where: { user: $user }) {
    reserve { symbol name decimals underlyingAsset }
    scaledATokenBalance
    currentTotalDebt
    usageAsCollateralEnabledOnUser
  }
}
`;

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const address = (searchParams.get("address") ?? "").toLowerCase();
  const chain = searchParams.get("chain") ?? "";
  const mock = searchParams.get("mock") === "1";

  if (!address || !chain)
    return NextResponse.json(
      { error: "address, chain requis" },
      { status: 400 }
    );
  if (mock) {
    const buf = await import("@/mocks/aave.mock.json");
    return NextResponse.json({
      chain,
      address,
      data: buf.default?.data ?? buf.data ?? {},
    });
  }
  const url = SUBGRAPHS[chain];
  if (!url)
    return NextResponse.json(
      { error: `Subgraph non supporté pour ${chain}` },
      { status: 400 }
    );

  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ query: QUERY, variables: { user: address } }),
  });
  if (!res.ok)
    return NextResponse.json(
      { error: `Subgraph ${res.status}` },
      { status: 500 }
    );
  const data = await res.json();
  return NextResponse.json({ chain, address, data: data?.data ?? {} });
}
