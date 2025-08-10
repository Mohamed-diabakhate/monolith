export type RiskParams = {
  minHealthFactor: number; // trigger protect actions below
  targetHealthFactor: number; // aim to restore to
};

export const defaultRisk: RiskParams = {
  minHealthFactor: 1.7,
  targetHealthFactor: 1.9,
};
