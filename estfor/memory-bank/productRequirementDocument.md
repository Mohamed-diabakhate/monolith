# Product Requirement Document (PRD)

## Title: NFT Listings & Sales Data Extractor for PaintSwap

1. Purpose

The purpose of this tool is to provide a scripted solution to fetch, enrich, and output NFT listings and sales data from the PaintSwap marketplace for a specific collection, entirely via the PaintSwap REST API.

The tool must:
• Retrieve active listings for a given NFT collection.
• Retrieve recent sales history for the same collection.
• Extract and normalize NFT traits from metadata.
• Enrich sales data with transaction value in both native token and USD.
• Output results databases in MongoDB.

⸻

2. Scope

In-Scope
• Fetching listings from the PaintSwap API (no on-chain calls).
• Parsing NFT metadata (IPFS or HTTP URIs) to extract traits.
• Configurable IPFS gateway fallback.
• Handling pagination and rate limits.

Out-of-Scope
• Buying/selling NFTs.
• Sales data.
• Direct blockchain interactions (e.g., contract calls).
• Historical trait change tracking.
• Historical sales data.

⸻

3. Users

Role Needs
Analyst Pull bulk listings for market insights.
Trader Identify NFT opportunities quickly with trait filtering.
Developer Integrate PaintSwap NFT data into dashboards, bots, or alerts.

⸻

4. Functional Requirements

4.1 Inputs
• collectionAddress (string, required): Ethereum-style checksum address.
• network (enum, required): "sonic" or "fantom".
• limit (int, optional): Max results per request (default 200).
• fromTimestamp, toTimestamp (int, optional): UNIX seconds for sales filtering.
• nativeDecimals (int, optional): Decimal precision (default 18).
• nativeSymbol (string, optional): Token symbol (default depends on network).
• ipfsGateway (string, optional): Base URL for IPFS fetches.
• sleepMs (int, optional): Delay between requests (for rate limiting).

⸻

4.2 Listings Retrieval
• Endpoint: GET https://api.paintswap.finance/sales
• Parameters: network, status=active; client filters by collectionAddress; pagination via cursor keys.
• Pagination: Loop until nextCursor is null/empty.
• Data to Capture:
• listingId, tokenId, seller, priceWei, priceHuman (wei / 1e18), createdAt, nft.name, nft.attributes[].

⸻

4.3 Metadata & Traits
• Preferred Source: Inline metadata from listings API.
• Fallback: Fetch tokenUri JSON from IPFS/HTTP.
• Parsing: Extract attributes[] array into { trait_type, value } pairs.

⸻

4.4 Output

Listings JSON

[
{
"tokenId": "42",
"collectionAddress": "0xABCD...1234",
"network": "sonic",
"listingId": "123456",
"seller": "0xSELLER...FEED",
"priceWei": "250000000000000000",
"listedAt": 1729876543,
"traits": [
{"trait_type": "Species", "value": "Humfinch"},
{"trait_type": "Tier", "value": "3"}
]
}
]

    •	CSV Option: Flatten traits into traits.<type> columns.

⸻

5. Non-Functional Requirements
   • Performance: Fetch 1,000+ listings within 30 seconds (subject to rate limits).
   • Resilience: Retry failed requests (3x) with exponential backoff.
   • Extensibility: Allow additional PaintSwap endpoints without breaking existing calls.
   • Portability: Run via Node.js or Python CLI.
   • Security: No private keys or wallet signing required.

⸻

6. Success Criteria
   • Works with Estfor Kingdom Pets on Sonic and any PaintSwap collection on Fantom.
   • Retrieves 100% of active listings and recent sales within specified window.
   • Includes normalized traits for each NFT.
   • Outputs USD values based on latest token price or manual override.
