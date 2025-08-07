"""
Tests for enhanced asset endpoints with EstFor game integration.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.main import app
from app.models.enhanced_asset import (
    EstForAsset,
    AssetCategory,
    RarityTier,
    EstForBoostEffect,
)
from app.game_constants import (
    Skill,
    EquipPosition,
    BoostType,
    BRONZE_HELMET,
    IRON_HELMET,
)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_enhanced_asset():
    """Create a sample enhanced asset for testing."""
    return EstForAsset(
        id="test_asset_1",
        asset_id="asset_123",
        item_id=BRONZE_HELMET,
        name="Bronze Helmet",
        description="A basic helmet made of bronze",
        category=AssetCategory.HELMET,
        equip_position=EquipPosition.HEAD,
        rarity_tier=RarityTier.COMMON,
        skill_requirements={"DEFENCE": 1},
        boost_effects=[
            EstForBoostEffect(
                boost_type=BoostType.COMBAT_XP,
                value=10,
                duration=3600
            )
        ],
        combat_stats={"defence": 5},
        compatible_skills=["DEFENCE", "COMBAT"],
        required_level=1,
        tradeable=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestEnhancedAssetEndpoints:
    """Test enhanced asset endpoints."""
    
    @patch('app.database.enhanced.enhanced_asset_db.list_enhanced_assets')
    def test_get_assets_with_filters(self, mock_list_assets, client, sample_enhanced_asset):
        """Test getting assets with various filters."""
        mock_list_assets.return_value = [sample_enhanced_asset]
        
        response = client.get(
            "/assets/?category=helmet&equip_position=1&min_rarity=1&tradeable_only=true"
        )
        assert response.status_code == 200
        
        assets = response.json()
        assert len(assets) == 1
        assert assets[0]["name"] == "Bronze Helmet"
        assert assets[0]["category"] == "helmet"
        assert assets[0]["equip_position"] == "HEAD"
        assert assets[0]["rarity_tier"] == "COMMON"
        assert assets[0]["tradeable"] is True
    
    @patch('app.database.enhanced.enhanced_asset_db.get_enhanced_asset')
    def test_get_asset_by_id(self, mock_get_asset, client, sample_enhanced_asset):
        """Test getting a specific asset by ID."""
        mock_get_asset.return_value = sample_enhanced_asset
        
        response = client.get("/assets/test_asset_1")
        assert response.status_code == 200
        
        asset = response.json()
        assert asset["id"] == "test_asset_1"
        assert asset["name"] == "Bronze Helmet"
        assert asset["item_id"] == BRONZE_HELMET
        assert asset["skill_requirements"]["DEFENCE"] == 1
    
    @patch('app.database.enhanced.enhanced_asset_db.get_enhanced_asset')
    def test_get_asset_not_found(self, mock_get_asset, client):
        """Test getting a non-existent asset."""
        mock_get_asset.return_value = None
        
        response = client.get("/assets/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch('app.services.estfor_client.estfor_client.get_assets')
    @patch('app.database.enhanced.enhanced_asset_db.store_enhanced_asset')
    @patch('app.services.asset_enrichment.asset_enrichment_service.enrich_asset')
    def test_collect_assets(self, mock_enrich, mock_store, mock_get_api_assets, client, sample_enhanced_asset):
        """Test collecting and enriching assets from API."""
        # Mock API response
        mock_get_api_assets.return_value = [
            {
                "id": "api_asset_1",
                "name": "Test Item",
                "type": "equipment",
                "metadata": {"rarity": "common"}
            }
        ]
        
        # Mock enrichment service
        mock_enrich.return_value = sample_enhanced_asset
        
        # Mock database storage
        mock_store.return_value = "stored_asset_id"
        
        response = client.post("/assets/collect")
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "completed"
        assert result["total_assets"] == 1
        assert result["enriched_count"] == 1
        assert result["stored_count"] == 1
        assert "enhancement" in result
    
    @patch('app.database.enhanced.enhanced_asset_db.search_enhanced_assets')
    def test_search_assets(self, mock_search, client, sample_enhanced_asset):
        """Test searching assets by query."""
        mock_search.return_value = [sample_enhanced_asset]
        
        response = client.get("/assets/search?q=bronze&category=helmet")
        assert response.status_code == 200
        
        assets = response.json()
        assert len(assets) == 1
        assert assets[0]["name"] == "Bronze Helmet"
    
    @patch('app.database.enhanced.enhanced_asset_db.list_enhanced_assets')
    def test_get_equipment_by_position(self, mock_list_assets, client, sample_enhanced_asset):
        """Test getting equipment by position."""
        mock_list_assets.return_value = [sample_enhanced_asset]
        
        response = client.get("/assets/equipment/1")  # HEAD position
        assert response.status_code == 200
        
        assets = response.json()
        assert len(assets) == 1
        assert assets[0]["equip_position"] == "HEAD"
    
    @patch('app.database.enhanced.enhanced_asset_db.get_assets_by_skill')
    def test_get_assets_by_skill(self, mock_get_by_skill, client, sample_enhanced_asset):
        """Test getting assets by skill requirement."""
        mock_get_by_skill.return_value = [sample_enhanced_asset]
        
        response = client.get("/assets/by-skill/defence?max_level=5")
        assert response.status_code == 200
        
        assets = response.json()
        assert len(assets) == 1
        assert "DEFENCE" in assets[0]["skill_requirements"]
    
    def test_get_assets_by_invalid_skill(self, client):
        """Test getting assets by invalid skill name."""
        response = client.get("/assets/by-skill/invalid_skill")
        assert response.status_code == 400
        assert "Invalid skill name" in response.json()["detail"]
    
    @patch('app.database.enhanced.enhanced_asset_db.get_asset_stats')
    def test_get_asset_categories(self, mock_get_stats, client):
        """Test getting asset categories with counts."""
        mock_get_stats.return_value.by_category = {
            "helmet": 10,
            "weapon": 15,
            "armor": 8
        }
        
        response = client.get("/assets/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert categories["helmet"] == 10
        assert categories["weapon"] == 15
        assert categories["armor"] == 8
    
    @patch('app.database.enhanced.enhanced_asset_db.get_assets_with_boosts')
    def test_get_assets_with_boosts(self, mock_get_boosts, client, sample_enhanced_asset):
        """Test getting assets with boost effects."""
        mock_get_boosts.return_value = [sample_enhanced_asset]
        
        response = client.get("/assets/boosts?boost_type=2")  # COMBAT_XP
        assert response.status_code == 200
        
        assets = response.json()
        assert len(assets) == 1
        assert len(assets[0]["boost_effects"]) > 0
    
    @patch('app.database.enhanced.enhanced_asset_db.get_enhanced_asset')
    def test_check_asset_compatibility_success(self, mock_get_asset, client, sample_enhanced_asset):
        """Test checking asset compatibility - player can equip."""
        mock_get_asset.return_value = sample_enhanced_asset
        
        player_skills = {"DEFENCE": 5, "MELEE": 10}
        
        response = client.post("/assets/compatible", json={
            "asset_id": "test_asset_1",
            "player_skills": player_skills
        })
        assert response.status_code == 200
        
        result = response.json()
        assert result["compatible"] is True
        assert result["asset_name"] == "Bronze Helmet"
        assert len(result["missing_requirements"]) == 0
        assert result["is_equipment"] is True
    
    @patch('app.database.enhanced.enhanced_asset_db.get_enhanced_asset')
    def test_check_asset_compatibility_failure(self, mock_get_asset, client, sample_enhanced_asset):
        """Test checking asset compatibility - player cannot equip."""
        mock_get_asset.return_value = sample_enhanced_asset
        
        player_skills = {"DEFENCE": 0, "MELEE": 10}
        
        response = client.post("/assets/compatible", json={
            "asset_id": "test_asset_1",
            "player_skills": player_skills
        })
        assert response.status_code == 200
        
        result = response.json()
        assert result["compatible"] is False
        assert "DEFENCE" in result["missing_requirements"]
        assert result["missing_requirements"]["DEFENCE"] == 1
    
    @patch('app.database.enhanced.enhanced_asset_db.get_asset_stats')
    def test_get_asset_stats(self, mock_get_stats, client):
        """Test getting comprehensive asset statistics."""
        from app.models.enhanced_asset import AssetStatsSummary
        
        mock_stats = AssetStatsSummary(
            total_assets=100,
            by_category={"helmet": 20, "weapon": 30},
            by_rarity={"1": 50, "2": 30, "3": 20},
            by_equip_position={"1": 20, "9": 30},
            equipment_count=80,
            consumable_count=15,
            material_count=5,
            with_boosts=25,
            tradeable_count=90
        )
        mock_get_stats.return_value = mock_stats
        
        response = client.get("/assets/stats/summary")
        assert response.status_code == 200
        
        stats = response.json()
        assert stats["total_assets"] == 100
        assert stats["equipment_count"] == 80
        assert stats["with_boosts"] == 25
    
    @patch('app.database.enhanced.enhanced_asset_db.bulk_migrate_legacy_assets')
    def test_migrate_legacy_assets(self, mock_migrate, client):
        """Test migrating legacy assets."""
        mock_migrate.return_value = {"migrated": 50, "failed": 5}
        
        response = client.post("/assets/migrate?limit=100")
        assert response.status_code == 200
        
        result = response.json()
        assert result["migrated_count"] == 50
        assert result["failed_count"] == 5
        assert result["status"] == "completed"


class TestAssetEnrichment:
    """Test asset enrichment functionality."""
    
    def test_enrich_helmet_asset(self):
        """Test enriching a helmet asset."""
        from app.services.asset_enrichment import asset_enrichment_service
        
        raw_asset = {
            "id": "helmet_123",
            "name": "Bronze Helmet",
            "type": "equipment",
            "item_id": BRONZE_HELMET,
            "metadata": {
                "rarity": "common",
                "requirements": {"defence": 1}
            }
        }
        
        enriched = asset_enrichment_service.enrich_asset(raw_asset)
        
        assert enriched.name == "Bronze Helmet"
        assert enriched.item_id == BRONZE_HELMET
        assert enriched.category == AssetCategory.HELMET
        assert enriched.equip_position == EquipPosition.HEAD
        assert enriched.rarity_tier == RarityTier.COMMON
        assert "DEFENCE" in enriched.skill_requirements
        assert "DEFENCE" in enriched.compatible_skills
    
    def test_enrich_unknown_item(self):
        """Test enriching an unknown item type."""
        from app.services.asset_enrichment import asset_enrichment_service
        
        raw_asset = {
            "id": "unknown_123",
            "name": "Mystery Item",
            "type": "unknown",
            "metadata": {}
        }
        
        enriched = asset_enrichment_service.enrich_asset(raw_asset)
        
        assert enriched.name == "Mystery Item"
        assert enriched.category == AssetCategory.UNKNOWN
        assert enriched.equip_position is None
        assert enriched.rarity_tier == RarityTier.COMMON
    
    def test_bulk_enrich_assets(self):
        """Test bulk enrichment of multiple assets."""
        from app.services.asset_enrichment import asset_enrichment_service
        
        raw_assets = [
            {
                "id": "helmet_1",
                "name": "Bronze Helmet",
                "item_id": BRONZE_HELMET,
            },
            {
                "id": "helmet_2", 
                "name": "Iron Helmet",
                "item_id": IRON_HELMET,
            }
        ]
        
        enriched_assets = asset_enrichment_service.bulk_enrich_assets(raw_assets)
        
        assert len(enriched_assets) == 2
        assert all(asset.category == AssetCategory.HELMET for asset in enriched_assets)
        assert all(asset.equip_position == EquipPosition.HEAD for asset in enriched_assets)


class TestAssetModels:
    """Test asset model functionality."""
    
    def test_asset_skill_requirements(self, sample_enhanced_asset):
        """Test asset skill requirement checking."""
        # Player has sufficient skills
        player_skills = {"DEFENCE": 5, "MELEE": 10}
        assert sample_enhanced_asset.can_equip_with_skills(player_skills) is True
        
        # Player lacks required skill
        player_skills = {"DEFENCE": 0, "MELEE": 10}
        assert sample_enhanced_asset.can_equip_with_skills(player_skills) is False
    
    def test_asset_boost_effects(self, sample_enhanced_asset):
        """Test asset boost effect functionality."""
        # Test boost applies to combat skill
        combat_boosts = sample_enhanced_asset.get_relevant_boosts(Skill.MELEE)
        assert len(combat_boosts) == 1
        assert combat_boosts[0].boost_type == BoostType.COMBAT_XP
        
        # Test boost doesn't apply to non-combat skill
        gathering_boosts = sample_enhanced_asset.get_relevant_boosts(Skill.MINING)
        assert len(gathering_boosts) == 0
    
    def test_asset_classification(self, sample_enhanced_asset):
        """Test asset classification methods."""
        assert sample_enhanced_asset.is_equipment() is True
        assert sample_enhanced_asset.is_consumable() is False
        assert sample_enhanced_asset.is_material() is False
    
    def test_asset_display_stats(self, sample_enhanced_asset):
        """Test asset display statistics."""
        stats = sample_enhanced_asset.get_display_stats()
        
        assert stats["name"] == "Bronze Helmet"
        assert stats["category"] == "helmet"
        assert stats["rarity"] == "COMMON"
        assert stats["equip_slot"] == "HEAD"
        assert "requirements" in stats
        assert "boosts" in stats
        assert "combat" in stats


class TestAssetFilters:
    """Test asset filtering functionality."""
    
    def test_asset_filter_query_building(self):
        """Test building MongoDB queries from filters."""
        from app.models.enhanced_asset import AssetFilter
        
        asset_filter = AssetFilter(
            category=AssetCategory.HELMET,
            equip_position=EquipPosition.HEAD,
            min_rarity=RarityTier.COMMON,
            max_rarity=RarityTier.RARE,
            required_skill="DEFENCE",
            max_skill_level=10,
            tradeable_only=True
        )
        
        query = asset_filter.build_query()
        
        assert query["category"] == "helmet"
        assert query["equip_position"] == 1
        assert query["rarity_tier"]["$gte"] == 1
        assert query["rarity_tier"]["$lte"] == 3
        assert "skill_requirements.DEFENCE" in query
        assert query["tradeable"] is True
    
    def test_equipment_only_filter(self):
        """Test equipment-only filtering."""
        from app.models.enhanced_asset import AssetFilter
        
        asset_filter = AssetFilter(equipment_only=True)
        query = asset_filter.build_query()
        
        assert query["equip_position"]["$ne"] is None
    
    def test_consumable_only_filter(self):
        """Test consumable-only filtering."""
        from app.models.enhanced_asset import AssetFilter
        
        asset_filter = AssetFilter(consumable_only=True)
        query = asset_filter.build_query()
        
        assert "$in" in query["category"]
        assert "consumable" in query["category"]["$in"]