# EstFor Elephant-Mongo Integration

This document describes the integration of EstFor with the shared `services/elephant-mongo` MongoDB service.

## Overview

The EstFor application has been migrated from using its own dedicated MongoDB container to connecting to the shared elephant-mongo service. This provides:

- **Centralized Database Management**: All applications can share the same MongoDB instance
- **Resource Efficiency**: No duplicate MongoDB containers
- **Consistent Configuration**: Shared authentication and networking setup
- **Auto-Shutdown**: Smart watchdog functionality from elephant-mongo

## Configuration Changes

### Database Connection Details

The EstFor application now connects to elephant-mongo with:

- **Host**: `mongo` (within docker network `dev_net`)
- **Port**: `27017`
- **Database**: `estfor` (created in elephant-mongo)
- **Username**: `Mohamed`
- **Password**: `Mohamed`
- **Auth Source**: `estfor`

### Connection URI

```
mongodb://Mohamed:Mohamed@mongo:27017/estfor?authSource=estfor
```

## Files Changed

### Configuration Files

1. **`app/config.py`**: Updated default MongoDB settings
2. **`env.example`**: Updated with elephant-mongo connection details
3. **`env.production.template`**: Updated production configuration
4. **`pytest.ini`**: Updated test database configuration

### Docker Configuration

1. **`docker-compose.yml`**: 
   - Removed standalone MongoDB service
   - Added `dev_net` network connection for elephant-mongo access
   - Removed MongoDB dependencies from health checks

### Test Configuration

1. **`tests/conftest.py`**: Updated to use `estfor_test` database name

### Initialization

1. **`mongo-init/init.js`**: Updated for `estfor` database (though no longer actively used)

## Network Setup

The EstFor services now connect to two networks:

1. **`estfor-network`**: Internal network for EstFor services
2. **`dev_net`**: External network to communicate with elephant-mongo

## Prerequisites

Before starting EstFor, ensure elephant-mongo is running:

```bash
cd /Users/mo/creative_home/services/elephant-mongo
docker-compose up -d
```

## Starting EstFor

The EstFor services will automatically connect to elephant-mongo:

```bash
cd /Users/mo/creative_home/monolith/estfor
docker-compose up -d
```

## Database Initialization

The EstFor application will automatically:

1. Connect to the `estfor` database in elephant-mongo
2. Create the `all_assets` collection if it doesn't exist
3. Set up appropriate indexes for performance

## Environment Variables

Key environment variables for elephant-mongo integration:

```bash
MONGODB_URI=mongodb://Mohamed:Mohamed@mongo:27017/estfor?authSource=estfor
MONGODB_DATABASE=estfor
MONGODB_COLLECTION=all_assets
```

## Testing

Tests use a separate database `estfor_test` to avoid conflicts:

```bash
MONGODB_URI=mongodb://Mohamed:Mohamed@localhost:27017/estfor_test?authSource=estfor_test
MONGODB_DATABASE=estfor_test
MONGODB_COLLECTION=all_assets_test
```

## Troubleshooting

### Connection Issues

1. **Check elephant-mongo status**:
   ```bash
   cd services/elephant-mongo
   docker-compose ps
   ```

2. **Verify network connectivity**:
   ```bash
   docker network ls | grep dev_net
   ```

3. **Check EstFor logs**:
   ```bash
   cd monolith/estfor
   docker-compose logs app
   ```

### Database Access

Connect to MongoDB directly to verify setup:

```bash
docker exec -it mongo mongosh --host mongo -u Mohamed -p Mohamed --authenticationDatabase estfor
```

Then verify the database:
```javascript
use estfor
show collections
db.all_assets.find().limit(5)
```

## Migration Notes

- **Data Migration**: No automatic data migration is performed. Existing EstFor data in the old MongoDB container would need to be manually migrated if required.
- **Backward Compatibility**: The application maintains the same API and behavior, only the database connection has changed.
- **Development**: For local development, you can still override the MongoDB URI in your `.env` file to point to a local instance.

## Benefits

1. **Resource Efficiency**: Shared MongoDB instance reduces memory and CPU usage
2. **Centralized Management**: One place to manage MongoDB configuration
3. **Auto-Shutdown**: Elephant-mongo's watchdog automatically shuts down MongoDB when not in use
4. **Consistent Environment**: All services use the same MongoDB setup
