import { z } from "zod";
import * as dotenv from "dotenv";

dotenv.config();

const envSchema = z.object({
  ARBITRUM_RPC: z.string().url(),
  SONIC_RPC: z.string().url(),
  ARBITRUM_AAVE_POOL: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
  SONIC_AAVE_POOL: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
  PRIVATE_KEY: z.string().regex(/^0x[a-fA-F0-9]{64}$/).optional(),
  SAFE_ADDRESS_ARBITRUM: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
  SAFE_ADDRESS_SONIC: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
  ALERT_WEBHOOK: z.string().optional(),
});

export type Env = z.infer<typeof envSchema>;

export function loadEnv(): Env {
  const parsed = envSchema.safeParse(process.env);
  if (!parsed.success) {
    const issues = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ");
    throw new Error(`Invalid environment: ${issues}`);
  }
  return parsed.data;
}
