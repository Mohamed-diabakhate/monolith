# Firestore Database Fix: Using "develop" Database

## Problem

The application was encountering a 403 Permission denied error when trying to access Firestore:

```
Failed to store NFT data: 403 Permission denied on resource project "digital-africa-rainbow". 
[reason: "CONSUMER_INVALID" domain: "googleapis.com" ...]
```

The root cause was that the default Firestore database was linked to an App Engine application that was disabled:

```
The database (default) is disabled for project digital-africa-rainbow. 
The database has an App Engine app and this app is disabled. 
Please refer to https://cloud.google.com/firestore/docs/app-engine-requirement 
to unlink your database from App Engine
```

## Solution

The application has been updated to use a separate "develop" database instead of the default database. This avoids the App Engine dependency issues.

### Changes Made

1. **Updated FirestoreManager** (`src/firestore_manager.py`):
   - Added `database_name` parameter to constructor
   - Default database name set to "develop"
   - Updated Firestore client initialization to use specified database

2. **Updated EnhancedNFTProcessor** (`src/enhanced_nft_processor.py`):
   - Added `database_name` parameter to constructor
   - Reads database name from environment variable `FIRESTORE_DATABASE`
   - Passes database name to FirestoreManager

3. **Updated main_enhanced.py**:
   - Added `--database` command line argument
   - Reads database name from environment variable `FIRESTORE_DATABASE`
   - Passes database name to EnhancedNFTProcessor

4. **Updated environment configuration**:
   - Added `FIRESTORE_DATABASE=develop` to `env.example`
   - Removed problematic `GOOGLE_APPLICATION_CREDENTIALS` setting from `.env`
   - Fixed quoted project ID in `.env`

## Usage

### Environment Variable (Recommended)

```bash
export FIRESTORE_DATABASE=develop
python main_enhanced.py --wallet YOUR_WALLET --firestore-only
```

### Command Line Argument

```bash
python main_enhanced.py --wallet YOUR_WALLET --database develop --firestore-only
```

### Environment File (.env)

```bash
# Add to your .env file
FIRESTORE_DATABASE=develop
```

## Verification

The fix has been tested and verified:

1. **Connection Test**: Successfully connects to "develop" database
2. **Write Test**: Successfully writes test data to "develop" database
3. **NFT Processing**: Successfully processed 638 NFTs from a test wallet
4. **Error Resolution**: No more 403 permission errors

### Test Results

```bash
# Test with wallet containing NFTs
export FIRESTORE_DATABASE=develop
python main_enhanced.py --wallet 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM --firestore-only

# Results:
# Total NFTs found: 638
# Successfully stored: 638
# Failed to store: 0
# Firestore sync success rate: 100.0%
```

## Benefits

1. **Avoids App Engine Issues**: No dependency on disabled App Engine applications
2. **Clean Separation**: Development data separate from production
3. **Better Permissions**: Simpler permission model without App Engine complexity
4. **Future-Proof**: Works regardless of App Engine status

## Creating the "develop" Database

If the "develop" database doesn't exist, create it:

```bash
gcloud firestore databases create --project=your-project-id --database=develop
```

## Migration from Default Database

If you have existing data in the default database and want to migrate:

1. Export data from default database
2. Create "develop" database
3. Import data to "develop" database
4. Update application configuration to use "develop" database

## Troubleshooting

### Still Getting Permission Errors

1. Ensure you're using the "develop" database:
   ```bash
   echo $FIRESTORE_DATABASE
   # Should output: develop
   ```

2. Check Google Cloud authentication:
   ```bash
   gcloud auth application-default login
   ```

3. Verify project permissions:
   ```bash
   gcloud projects get-iam-policy your-project-id
   ```

### Database Doesn't Exist

Create the "develop" database:
```bash
gcloud firestore databases create --project=your-project-id --database=develop
```

### Environment Variable Not Set

Check your environment:
```bash
# Should show: develop
echo $FIRESTORE_DATABASE

# If not set, set it:
export FIRESTORE_DATABASE=develop
```

## Configuration Reference

| Method | Setting | Example |
|--------|---------|---------|
| Environment Variable | `FIRESTORE_DATABASE` | `export FIRESTORE_DATABASE=develop` |
| Command Line | `--database` | `--database develop` |
| .env File | `FIRESTORE_DATABASE` | `FIRESTORE_DATABASE=develop` |

## Default Behavior

- If no database is specified, the application defaults to "develop"
- This ensures compatibility and avoids App Engine issues
- The default can be overridden using any of the configuration methods above 