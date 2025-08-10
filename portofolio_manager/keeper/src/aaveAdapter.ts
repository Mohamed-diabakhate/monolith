import { Address, Hex, PublicClient } from "viem";

// Minimal subset of IPool ABI for read-only account data
const POOL_ABI = [
  {
    "inputs": [
      { "internalType": "address", "name": "user", "type": "address" }
    ],
    "name": "getUserAccountData",
    "outputs": [
      { "internalType": "uint256", "name": "totalCollateralBase", "type": "uint256" },
      { "internalType": "uint256", "name": "totalDebtBase", "type": "uint256" },
      { "internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256" },
      { "internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256" },
      { "internalType": "uint256", "name": "ltv", "type": "uint256" },
      { "internalType": "uint256", "name": "healthFactor", "type": "uint256" }
    ],
    "stateMutability": "view",
    "type": "function"
  }
] as const;

export type AccountData = {
  totalCollateralBase: bigint;
  totalDebtBase: bigint;
  availableBorrowsBase: bigint;
  currentLiquidationThreshold: bigint;
  ltv: bigint;
  healthFactorRay: bigint; // 18 decimals
};

export async function readAccountData(
  client: PublicClient,
  pool: Address,
  user: Address
): Promise<AccountData> {
  const [totalCollateralBase, totalDebtBase, availableBorrowsBase, currentLiquidationThreshold, ltv, healthFactor] =
    await client.readContract({ address: pool, abi: POOL_ABI, functionName: "getUserAccountData", args: [user] });
  return {
    totalCollateralBase,
    totalDebtBase,
    availableBorrowsBase,
    currentLiquidationThreshold,
    ltv,
    healthFactorRay: healthFactor,
  };
}

export function rayToFloatRay(x: bigint): number {
  // health factor is WadRayMath ray (1e18)
  const RAY = 10n ** 18n;
  return Number(x) / Number(RAY);
}
