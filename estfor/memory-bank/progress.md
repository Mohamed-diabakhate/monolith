### What works

- Baseline `systemPatterns.md` created with four key sections.

### PaintSwap Extractor – Milestones

- Phase 1: Listings Ingestion
  - PaintSwap client with pagination and retry/backoff
  - Inline metadata usage with IPFS fallback
  - Trait normalization and flattening
  - MongoDB collections and indexes

- Phase 2: Sales Enrichment
  - Recent sales endpoint integration with time window
  - Price conversion (native ↔ USD) via cached price feed
  - Join listings/sales where applicable

- Phase 3: CLI & Ops
  - Typer CLI with PRD parameters (collectionAddress, network, etc.)
  - Metrics and structured logging
  - Config via `.env` and flags; k6 perf script update

### What's left

- Implement Phase 1 modules and tests
- Confirm PaintSwap REST endpoints and response shapes
- Define MongoDB indexes and validate perf targets

### Status

- In progress

### Known issues

- PaintSwap API rate limits may require tuning sleep/backoff
