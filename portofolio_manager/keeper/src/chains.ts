import { createPublicClient, http, Address, PublicClient } from "viem";
import { arbitrum } from "viem/chains";

export type ChainKey = "arbitrum" | "sonic";

export type ChainContext = {
  key: ChainKey;
  client: PublicClient;
  aavePool: Address;
};

export function makeChains(env: {
  ARBITRUM_RPC: string;
  SONIC_RPC: string;
  ARBITRUM_AAVE_POOL: string;
  SONIC_AAVE_POOL: string;
}): Record<ChainKey, ChainContext> {
  const arb: ChainContext = {
    key: "arbitrum",
    client: createPublicClient({ chain: arbitrum, transport: http(env.ARBITRUM_RPC) }),
    aavePool: env.ARBITRUM_AAVE_POOL as Address,
  };

  // Sonic is not in viem by default; define minimal chain object
  const sonicChain = {
    id: 570,
    name: "Sonic",
    network: "sonic",
    nativeCurrency: { name: "S", symbol: "S", decimals: 18 },
    rpcUrls: { default: { http: [env.SONIC_RPC] } },
  } as any;

  const sonic: ChainContext = {
    key: "sonic",
    // viem accepts custom chain-like objects; limit usage to PublicClient
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    client: createPublicClient({ chain: sonicChain, transport: http(env.SONIC_RPC) }),
    aavePool: env.SONIC_AAVE_POOL as Address,
  };

  return { arbitrum: arb, sonic };
}
