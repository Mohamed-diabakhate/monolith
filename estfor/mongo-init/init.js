// MongoDB initialization script for EstFor Asset Collection System
// Note: This script is no longer used as we're connecting to services/elephant-mongo
// which now provides the 'estfor' database with user 'Mohamed'

// Switch to the estfor database (created in elephant-mongo)
db = db.getSiblingDB("estfor");

// Create the all_assets collection
db.createCollection("all_assets");

// Create indexes for better performance
db.all_assets.createIndex({ created_at: -1 });
db.all_assets.createIndex({ updated_at: -1 });
db.all_assets.createIndex({ asset_id: 1 }, { unique: true });
db.all_assets.createIndex({ name: 1 });
db.all_assets.createIndex({ type: 1 });

// Create a compound index for common queries
db.all_assets.createIndex({ type: 1, created_at: -1 });

// Insert a sample document to verify the setup
db.all_assets.insertOne({
  asset_id: "sample_asset_001",
  name: "Sample Asset",
  type: "weapon",
  description: "This is a sample asset for testing",
  created_at: new Date(),
  updated_at: new Date(),
  metadata: {
    rarity: "common",
    level: 1,
  },
});

print("MongoDB initialization completed successfully");
print("Database: estfor (elephant-mongo)");
print("Collection: all_assets");
print("Indexes created for optimal performance");
