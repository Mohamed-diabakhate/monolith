"""
Tests for game assets API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.game_constants import Skill, EquipPosition, BoostType, BRONZE_HELMET, IRON_HELMET


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestGameAssetsAPI:
    """Test game assets API endpoints."""
    
    def test_get_helmets(self, client):
        """Test getting all helmet items."""
        response = client.get("/api/game/items/helmets")
        assert response.status_code == 200
        
        helmets = response.json()
        assert len(helmets) == 5
        
        # Check first helmet (Bronze)
        bronze = helmets[0]
        assert bronze["item_id"] == BRONZE_HELMET
        assert bronze["name"] == "Bronze Helmet"
        assert bronze["equip_position"] == EquipPosition.HEAD.value
        assert bronze["skill_requirements"]["5"] == 1  # Skill.DEFENCE = 5
    
    def test_get_specific_item(self, client):
        """Test getting a specific item by ID."""
        response = client.get(f"/api/game/items/{IRON_HELMET}")
        assert response.status_code == 200
        
        item = response.json()
        assert item["item_id"] == IRON_HELMET
        assert item["name"] == "Iron Helmet"
        assert item["equip_position"] == EquipPosition.HEAD.value
    
    def test_get_nonexistent_item(self, client):
        """Test getting a non-existent item."""
        response = client.get("/api/game/items/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_check_can_equip_success(self, client):
        """Test checking if player can equip an item (success case)."""
        player_data = {
            "skills": {
                str(Skill.DEFENCE.value): 15  # Defence level 15
            }
        }
        
        response = client.post(
            f"/api/game/player/can-equip?item_id={IRON_HELMET}",
            json=player_data
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["item_id"] == IRON_HELMET
        assert result["can_equip"] is True
        assert "DEFENCE" in result["player_skills"]
    
    def test_check_can_equip_failure(self, client):
        """Test checking if player can equip an item (failure case)."""
        player_data = {
            "skills": {
                str(Skill.DEFENCE.value): 5  # Defence level 5 (too low for Iron Helmet)
            }
        }
        
        response = client.post(
            f"/api/game/player/can-equip?item_id={IRON_HELMET}",
            json=player_data
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["item_id"] == IRON_HELMET
        assert result["can_equip"] is False
    
    def test_list_skills(self, client):
        """Test listing all skills."""
        response = client.get("/api/game/skills")
        assert response.status_code == 200
        
        skills = response.json()
        assert len(skills) > 10
        
        # Check that MINING is in the list
        mining_skills = [s for s in skills if s["name"] == "MINING"]
        assert len(mining_skills) == 1
        assert mining_skills[0]["id"] == Skill.MINING.value
        assert mining_skills[0]["display_name"] == "Mining"
    
    def test_list_skills_filtered(self, client):
        """Test listing skills filtered by category."""
        response = client.get("/api/game/skills?category=combat")
        assert response.status_code == 200
        
        skills = response.json()
        assert len(skills) == 5  # Combat skills only
        
        skill_names = [s["name"] for s in skills]
        assert "MELEE" in skill_names
        assert "RANGED" in skill_names
        assert "MAGIC" in skill_names
        assert "DEFENCE" in skill_names
        assert "HEALTH" in skill_names
    
    def test_list_boost_types(self, client):
        """Test listing boost types."""
        response = client.get("/api/game/boost-types")
        assert response.status_code == 200
        
        boosts = response.json()
        assert len(boosts) > 5
        
        # Check ANY_XP boost
        any_xp = [b for b in boosts if b["name"] == "ANY_XP"]
        assert len(any_xp) == 1
        assert any_xp[0]["id"] == BoostType.ANY_XP.value
        assert "all skills" in any_xp[0]["description"].lower()
    
    def test_calculate_boost_effect(self, client):
        """Test calculating boost effects."""
        boost_data = {
            "boost_type": BoostType.COMBAT_XP.value,
            "value": 50,
            "duration": 3600
        }
        
        # Test with combat skill (should apply)
        response = client.post(
            f"/api/game/boost/calculate-effect?skill={Skill.MELEE.value}",
            json=boost_data
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["boost_type"] == "COMBAT_XP"
        assert result["skill"] == "MELEE"
        assert result["applies"] is True
        assert result["value"] == 50
        
        # Test with non-combat skill (should not apply)
        response = client.post(
            f"/api/game/boost/calculate-effect?skill={Skill.MINING.value}",
            json=boost_data
        )
        assert response.status_code == 200
        
        result = response.json()
        assert result["boost_type"] == "COMBAT_XP"
        assert result["skill"] == "MINING"
        assert result["applies"] is False
        assert result["value"] == 0
    
    def test_list_equipment_slots(self, client):
        """Test listing equipment slots."""
        response = client.get("/api/game/equipment-slots")
        assert response.status_code == 200
        
        slots = response.json()
        assert len(slots) > 10
        
        # Check HEAD slot
        head_slot = [s for s in slots if s["name"] == "HEAD"]
        assert len(head_slot) == 1
        assert head_slot[0]["id"] == EquipPosition.HEAD.value
        assert "helmet" in head_slot[0]["description"].lower()