### Current focus

- Plan and implement the PaintSwap NFT Listings & Sales Extractor per `memory-bank/productRequirementDocument.md`.

### Recent changes

- Reviewed PRD and drafted implementation plan, milestones, and acceptance criteria.
- Added detailed task breakdown to `Tasks.md`.
- Extended `memory-bank/progress.md` with feature-specific milestones.

### Next steps

- Day 1–2:
  - Implement PaintSwap client and listings pagination loop.
  - Implement metadata parsing with IPFS fallback and trait normalization.
- Define MongoDB schemas and indexes; store listings. Added `priceHuman`, `name`, and `attributes` fields.
- Day 3–4:
- Integrate price source for USD conversion; implement recent sales retrieval. Base URL now `https://api.paintswap.finance` using `/sales/`.
  - Add retry/backoff, rate limiting, logging, and metrics.
  - Ship CLI with parameters from PRD and initial tests.
- Day 5:
  - Hardening and documentation; performance run (1,000+ listings in ~30s subject to rate limits).

### Decisions & assumptions

- Treat “recent sales” as in-scope (PRD Purpose and Success Criteria) despite an Out-of-Scope bullet referencing "Sales data"; that bullet refers to on-chain trading operations and historical backfills.
- Target Python CLI (Typer) for parity with the existing Python codebase; integrate with existing MongoDB config.
- Use configurable IPFS gateway with fallback order: inline metadata → primary gateway → secondary gateway.
- Token price source: coingecko or PaintSwap price API; cache prices during a run.
