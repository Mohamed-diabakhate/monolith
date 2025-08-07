import pino from "pino";
import { loadEnv } from "./config.js";
import { makeChains } from "./chains.js";
import { readAccountData, rayToFloatRay } from "./aaveAdapter.js";
import { defaultRisk } from "./risk.js";

const log = pino({ level: process.env.LOG_LEVEL ?? "info" });

async function checkUser(chainKey: "arbitrum" | "sonic", user: `0x${string}`) {
  const env = loadEnv();
  const chains = makeChains(env);
  const ctx = chains[chainKey];
  try {
    const data = await readAccountData(ctx.client, ctx.aavePool, user);
    const hf = rayToFloatRay(data.healthFactorRay);
    log.info({ chain: chainKey, user, hf, totalDebtBase: data.totalDebtBase.toString(), totalCollateralBase: data.totalCollateralBase.toString() }, "account data");
    if (hf > 0 && hf < defaultRisk.minHealthFactor) {
      log.warn({ chain: chainKey, user, hf }, "Health factor below threshold. Protective action required");
      // TODO: propose and execute repay/supply depending on balances and allowed assets
    }
  } catch (e) {
    log.error({ err: e, chain: chainKey }, "Failed to read account data");
  }
}

async function main() {
  const users = (process.env.USERS ?? "").split(",").map((s) => s.trim()).filter(Boolean) as `0x${string}`[];
  if (users.length === 0) {
    throw new Error("Set USERS=0xabc,0xdef to monitor");
  }
  const intervalMs = Number(process.env.INTERVAL_MS ?? 60000);
  for (;;) {
    await Promise.all([
      ...users.map((u) => checkUser("arbitrum", u)),
      ...users.map((u) => checkUser("sonic", u)),
    ]);
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

main().catch((e) => {
  log.error(e);
  process.exit(1);
});
