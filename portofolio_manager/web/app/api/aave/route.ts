import { NextRequest, NextResponse } from "next/server";
import { ethers } from "ethers";
import { UiPoolDataProvider } from "@aave/contract-helpers";
import * as markets from "@bgd-labs/aave-address-book";

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
  // On-chain via Aave UiPoolDataProvider
  type MarketDef = {
    UI_POOL_DATA_PROVIDER: string;
    POOL_ADDRESSES_PROVIDER: string;
  };
  const cfg =
    chain === "arbitrum-mainnet"
      ? {
          rpc: `https://rpc.ankr.com/arbitrum/${
            process.env.ANKR_API_KEY ?? ""
          }`,
          market: (markets as unknown as { AaveV3Arbitrum: MarketDef })
            .AaveV3Arbitrum,
          chainId: 42161,
        }
      : chain === "sonic-mainnet"
      ? {
          rpc: process.env.SONIC_RPC_URL as string,
          market: (markets as unknown as { AaveV3Sonic: MarketDef })
            .AaveV3Sonic,
          chainId: Number(process.env.SONIC_CHAIN_ID ?? 0),
        }
      : null;

  if (!cfg || !cfg.rpc || !cfg.market?.UI_POOL_DATA_PROVIDER) {
    return NextResponse.json(
      { error: `Unsupported chain or missing config: ${chain}` },
      { status: 400 }
    );
  }

  try {
    const provider = new ethers.providers.JsonRpcProvider(cfg.rpc);
    const ui = new UiPoolDataProvider({
      uiPoolDataProviderAddress: cfg.market.UI_POOL_DATA_PROVIDER,
      provider,
      chainId: cfg.chainId,
    });
    const userRes = await ui.getUserReservesHumanized({
      lendingPoolAddressProvider: cfg.market.POOL_ADDRESSES_PROVIDER,
      user: address,
    });
    return NextResponse.json({
      chain,
      address,
      data: { userReserves: userRes.userReserves },
    });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
