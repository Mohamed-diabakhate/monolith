# PaintSwap Listings & Sales Extractor — Task Breakdown

## Phase 1: Listings Ingestion
- Implement `PaintSwapClient` for listings
  - GET `https://api.paintswap.finance/v2/listings` with pagination (cursor)
  - Params: `collectionAddress`, `network`, `status=active`, `limit`
  - Retry/backoff (3 tries, exponential)
  - Optional `sleepMs` between pages
- Metadata & Traits
  - Prefer inline metadata from listings
  - Fallback: fetch `tokenUri` via IPFS/HTTP (configurable gateway)
  - Normalize `attributes[]` → `{trait_type, value}`; flatten map for CSV
- Persistence
  - Define MongoDB collection `paintswap_listings`
  - Indexes: `{collectionAddress:1, network:1, tokenId:1}`, `{listedAt:-1}`, `{priceWei:-1}`
  - Upsert by `{collectionAddress, network, listingId}`
- Testing
  - Unit tests for pagination, retry, trait parsing
  - Integration test with mocked API

Acceptance:
- 100% of active listings fetched for a known small collection
- Traits present for each listing (inline or via fallback)
- Time to fetch 1k listings ≤ 30s (subject to API limits)

## Phase 2: Sales Enrichment
- Sales endpoint integration (recent window)
  - Inputs: `fromTimestamp`, `toTimestamp`
  - Data: `tokenId`, `priceWei`, `buyer`, `seller`, `txHash`, `soldAt`
- Price conversion
  - Fetch native token price (Coingecko / PaintSwap)
  - Compute USD per sale and listing
  - Cache price during run
- Persistence
  - Collection: `paintswap_sales` with indexes `{collectionAddress, network, soldAt}`
- Testing
  - Unit tests for price conversion, time windows

Acceptance:
- Recent sales ingested within provided window
- USD values computed with current price

## Phase 3: CLI & Ops
- Typer-based CLI `paintswap-cli` with flags from PRD
- Structured logging, Prometheus counters/timers
- Config via `.env` + CLI overrides
- CSV export option (flattened traits)

Acceptance:
- CLI runs end-to-end: listings + optional sales
- Metrics exposed; logs structured

## Nice-to-haves
- Concurrency with bounded semaphore for metadata fetches
- Backoff jitter; adaptive rate limiting
- Resume from last cursor
