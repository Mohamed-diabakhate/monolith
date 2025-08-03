# Firestore Integration for NFT Gallery

## Overview

This document describes the Firestore integration that serves as a middle layer between the Helius API and local file storage for the NFT Gallery application. The integration provides a robust, scalable database solution for storing and managing NFT metadata.

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│   Helius    │───▶│  Firestore   │───▶│ Local File  │───▶│   User      │
│    API      │    │   Database   │    │   System    │    │  Interface  │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

### Data Flow

1. **Helius API**: Fetches raw NFT data using DAS (Digital Asset Standard) API
2. **Firestore**: Stores processed NFT metadata and serves as a cache/backup
3. **Local File System**: Downloads and stores NFT images locally
4. **User Interface**: Provides access to NFT data and images

## Firestore Document Structure

### Main Collection: `nfts`

Each NFT is stored as a document with the asset ID as the document ID.

```json
{
  "asset_id": "string",                    // Unique NFT identifier (document ID)
  "wallet_address": "string",              // Owner wallet address
  "name": "string",                        // NFT name
  "symbol": "string",                      // NFT symbol
  "description": "string",                 // NFT description
  "image_url": "string",                   // Primary image URL
  "metadata_uri": "string",                // Metadata URI (IPFS/Arweave)
  "attributes": [                          // NFT attributes/traits
    {
      "trait_type": "string",
      "value": "string"
    }
  ],
  "collection": {                          // Collection information
    "name": "string",
    "family": "string"
  },
  "compressed": false,                     // Whether NFT is compressed
  "royalties": [                           // Royalty information
    {
      "recipient": "string",
      "percentage": "number"
    }
  ],
  "creators": [                            // Creator information
    {
      "address": "string",
      "share": "number"
    }
  ],
  "supply": 1,                             // Total supply
  "decimals": 0,                           // Token decimals
  "token_standard": "string",              // Token standard (e.g., "NonFungible")
  "raw_data": {},                          // Complete raw data from Helius
  "created_at": "timestamp",               // Document creation time
  "updated_at": "timestamp",               // Last update time
  "last_synced": "timestamp",              // Last sync from Helius
  "sync_status": "string"                  // "synced", "failed", "pending", "downloaded"
}
```

### Secondary Collection: `wallet_summaries`

Summary information for each wallet.

```json
{
  "wallet_address": "string",              // Wallet address (document ID)
  "total_nfts": "number",                  // Total NFTs in wallet
  "last_sync": "timestamp",                // Last sync time
  "sync_status": "string",                 // "completed", "partial", "failed"
  "failed_count": "number",                // Number of failed syncs
  "updated_at": "timestamp"                // Last update time
}
```

## Key Features

### 1. Data Extraction and Storage

The `FirestoreManager` class extracts key information from Helius DAS API responses and stores them in a structured format:

- **Metadata Extraction**: Automatically extracts name, symbol, description, attributes, etc.
- **Image URL Resolution**: Handles multiple image URL sources (files array, links, metadata)
- **Collection Information**: Extracts collection name and family
- **Compression Support**: Tracks compressed NFT status
- **Royalty Tracking**: Stores royalty and creator information

### 2. Search and Query Capabilities

```python
# Search by wallet address
nfts = firestore_manager.get_nfts_by_wallet("wallet_address")

# Search with filters
nfts = firestore_manager.search_nfts(
    wallet_address="wallet_address",
    collection_name="Bored Ape Yacht Club",
    compressed=False,
    limit=100
)

# Get specific NFT
nft = firestore_manager.get_nft_by_asset_id("asset_id")
```

### 3. Sync Status Management

Tracks the synchronization status of each NFT:

- `synced`: Successfully synced from Helius
- `failed`: Failed to sync from Helius
- `pending`: Pending sync
- `downloaded`: Successfully downloaded to local storage
- `download_failed`: Failed to download to local storage

### 4. Statistics and Analytics

Provides comprehensive statistics:

```python
stats = firestore_manager.get_collection_stats("wallet_address")
# Returns:
# {
#   "total_nfts": 150,
#   "collections": {"Bored Ape": 50, "Doodles": 30, ...},
#   "compressed_count": 10,
#   "sync_status_counts": {"synced": 140, "failed": 10},
#   "recent_additions": [...]
# }
```

## Usage Examples

### Basic Integration

```python
from src.enhanced_nft_processor import EnhancedNFTProcessor

# Initialize processor
processor = EnhancedNFTProcessor(
    wallet_address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
    output_dir="~/Pictures/NFTs",
    project_id="your-gcp-project-id"
)

# Sync to Firestore only
sync_results = processor.sync_wallet_to_firestore()

# Process with Firestore integration (sync + download)
results = processor.process_wallet_with_firestore(download_images=True)

# Get Firestore statistics
stats = processor.get_firestore_stats()
```

### Advanced Queries

```python
from src.firestore_manager import FirestoreManager

firestore_manager = FirestoreManager(project_id="your-gcp-project-id")

# Get all NFTs from a specific collection
bored_apes = firestore_manager.search_nfts(
    collection_name="Bored Ape Yacht Club",
    limit=1000
)

# Get compressed NFTs only
compressed_nfts = firestore_manager.search_nfts(
    compressed=True,
    limit=100
)

# Get NFTs by wallet and collection
wallet_nfts = firestore_manager.search_nfts(
    wallet_address="wallet_address",
    collection_name="Doodles"
)
```

## Setup and Configuration

### 1. Google Cloud Project Setup

1. Create a Google Cloud project
2. Enable Firestore API
3. Create a Firestore database (Native mode recommended)
4. Set up authentication (Service Account or Application Default Credentials)

### 2. Environment Variables

```bash
# Required
export HELIUS_API_KEY="your-helius-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Optional
export OUTPUT_DIR="~/Pictures/NFTs"
```

### 3. Service Account Setup (Recommended)

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Benefits of Firestore Integration

### 1. Scalability
- Handles large NFT collections efficiently
- Automatic indexing for fast queries
- Real-time updates and synchronization

### 2. Data Persistence
- Reliable backup of NFT metadata
- No data loss during local file system issues
- Cross-device synchronization

### 3. Advanced Querying
- Complex filtering and search capabilities
- Collection-based analytics
- Historical data tracking

### 4. Performance
- Cached data reduces API calls to Helius
- Fast local queries
- Efficient pagination for large datasets

### 5. Monitoring and Analytics
- Sync status tracking
- Error monitoring
- Usage statistics

## Error Handling

The integration includes comprehensive error handling:

- **API Failures**: Graceful handling of Helius API errors
- **Network Issues**: Retry mechanisms for connectivity problems
- **Data Validation**: Validation of NFT data before storage
- **Firestore Errors**: Proper error handling for database operations

## Security Considerations

1. **Authentication**: Use service accounts with minimal required permissions
2. **Data Privacy**: NFT data is stored securely in Google Cloud
3. **Access Control**: Firestore security rules can be configured for additional protection
4. **API Keys**: Store sensitive keys in environment variables

## Monitoring and Maintenance

### 1. Sync Monitoring
- Track sync success/failure rates
- Monitor API rate limits
- Alert on sync failures

### 2. Data Quality
- Validate stored data integrity
- Monitor for duplicate entries
- Track data freshness

### 3. Performance Monitoring
- Query performance metrics
- Storage usage tracking
- API call optimization

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live NFT updates
2. **Advanced Analytics**: Price tracking, rarity analysis
3. **Multi-chain Support**: Extend to other blockchain networks
4. **User Management**: Multi-user support with access controls
5. **Backup and Recovery**: Automated backup strategies 