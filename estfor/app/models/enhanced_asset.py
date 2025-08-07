"""
Enhanced asset models with EstFor Kingdom game integration.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from app.game_constants import (
    Skill,
    EquipPosition,
    BoostType,
    ActivityType,
    CombatStyle,
)


class AssetCategory(str, Enum):
    """Asset categories based on EstFor game types."""
    WEAPON = "weapon"
    ARMOR = "armor" 
    HELMET = "helmet"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    TOOL = "tool"
    BOOST_VIAL = "boost_vial"
    FOOD = "food"
    SEED = "seed"
    LOG = "log"
    ORE = "ore"
    RUNE = "rune"
    UNKNOWN = "unknown"


class RarityTier(int, Enum):
    """Item rarity tiers."""
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


class EstForBoostEffect(BaseModel):
    """Represents a boost effect on an item."""
    boost_type: BoostType = Field(..., description="Type of boost")
    value: int = Field(..., description="Boost value (percentage or fixed)")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    
    def applies_to_skill(self, skill: Skill) -> bool:
        """Check if this boost applies to a specific skill."""
        if self.boost_type == BoostType.ANY_XP:
            return skill != Skill.NONE
        elif self.boost_type == BoostType.COMBAT_XP:
            return skill in [Skill.MELEE, Skill.RANGED, Skill.MAGIC, Skill.DEFENCE, Skill.HEALTH]
        elif self.boost_type == BoostType.NON_COMBAT_XP:
            return skill not in [Skill.NONE, Skill.COMBAT, Skill.MELEE, Skill.RANGED, 
                               Skill.MAGIC, Skill.DEFENCE, Skill.HEALTH]
        elif self.boost_type == BoostType.GATHERING:
            return skill in [Skill.MINING, Skill.WOODCUTTING, Skill.FISHING, 
                           Skill.FARMING, Skill.HUNTING]
        return False


class EstForAsset(BaseModel):
    """Enhanced asset model with EstFor Kingdom game integration."""
    # Basic identification
    id: str = Field(..., description="Database document ID")
    asset_id: Optional[str] = Field(None, description="Original asset ID from API")
    item_id: Optional[int] = Field(None, description="EstFor constant item ID")
    
    # Basic information
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    
    # Game-specific classification
    category: AssetCategory = Field(default=AssetCategory.UNKNOWN, description="Asset category")
    equip_position: Optional[EquipPosition] = Field(None, description="Where the item can be equipped")
    rarity_tier: RarityTier = Field(default=RarityTier.COMMON, description="Item rarity")
    
    # Requirements and effects
    skill_requirements: Dict[str, int] = Field(default_factory=dict, description="Required skill levels (skill_name: level)")
    boost_effects: List[EstForBoostEffect] = Field(default_factory=list, description="Item boost effects")
    combat_stats: Dict[str, int] = Field(default_factory=dict, description="Combat stats (attack, defence, etc.)")
    
    # Game compatibility
    compatible_skills: List[str] = Field(default_factory=list, description="Skills this item can be used with")
    required_level: Optional[int] = Field(None, description="Minimum level to use item")
    tradeable: bool = Field(default=True, description="Whether item can be traded")
    
    # Original API data (preserved for compatibility)
    type: Optional[str] = Field(None, description="Original asset type from API")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('equip_position', pre=True)
    def validate_equip_position(cls, v):
        """Validate equipment position."""
        if v is not None and isinstance(v, int):
            try:
                return EquipPosition(v)
            except ValueError:
                return None  # Invalid position becomes None
        return v
    
    @validator('category', pre=True)
    def validate_category(cls, v):
        """Validate and infer asset category."""
        if isinstance(v, str):
            # Try to match existing category
            for cat in AssetCategory:
                if v.lower() == cat.value:
                    return cat
        return AssetCategory.UNKNOWN
    
    def get_skill_requirement(self, skill: Union[Skill, str]) -> int:
        """Get the requirement for a specific skill."""
        if isinstance(skill, Skill):
            skill_name = skill.name
        else:
            skill_name = skill
        return self.skill_requirements.get(skill_name, 0)
    
    def can_equip_with_skills(self, player_skills: Dict[str, int]) -> bool:
        """Check if player meets skill requirements to equip this item."""
        for skill_name, required_level in self.skill_requirements.items():
            if player_skills.get(skill_name, 0) < required_level:
                return False
        return True
    
    def get_relevant_boosts(self, skill: Skill) -> List[EstForBoostEffect]:
        """Get boost effects that apply to a specific skill."""
        return [boost for boost in self.boost_effects if boost.applies_to_skill(skill)]
    
    def is_equipment(self) -> bool:
        """Check if this is an equipable item."""
        return self.equip_position is not None
    
    def is_consumable(self) -> bool:
        """Check if this is a consumable item."""
        return self.category in [AssetCategory.CONSUMABLE, AssetCategory.FOOD, AssetCategory.BOOST_VIAL]
    
    def is_material(self) -> bool:
        """Check if this is a crafting material."""
        return self.category in [AssetCategory.MATERIAL, AssetCategory.LOG, AssetCategory.ORE, AssetCategory.SEED]
    
    def get_display_stats(self) -> Dict[str, Any]:
        """Get formatted stats for display."""
        stats = {
            "name": self.name,
            "category": self.category.value,
            "rarity": self.rarity_tier.name,
        }
        
        if self.equip_position:
            stats["equip_slot"] = self.equip_position.name
            
        if self.skill_requirements:
            stats["requirements"] = self.skill_requirements
            
        if self.boost_effects:
            stats["boosts"] = [
                {
                    "type": boost.boost_type.name,
                    "value": boost.value,
                    "duration": boost.duration
                }
                for boost in self.boost_effects
            ]
            
        if self.combat_stats:
            stats["combat"] = self.combat_stats
            
        return stats


class AssetFilter(BaseModel):
    """Filtering options for asset queries."""
    category: Optional[AssetCategory] = Field(None, description="Filter by category")
    equip_position: Optional[EquipPosition] = Field(None, description="Filter by equipment position")
    min_rarity: Optional[RarityTier] = Field(None, description="Minimum rarity tier")
    max_rarity: Optional[RarityTier] = Field(None, description="Maximum rarity tier")
    required_skill: Optional[str] = Field(None, description="Filter by required skill")
    max_skill_level: Optional[int] = Field(None, description="Maximum skill level requirement")
    has_boost: Optional[BoostType] = Field(None, description="Filter by boost type")
    tradeable_only: Optional[bool] = Field(None, description="Only tradeable items")
    equipment_only: Optional[bool] = Field(None, description="Only equipable items")
    consumable_only: Optional[bool] = Field(None, description="Only consumable items")
    
    def build_query(self) -> Dict[str, Any]:
        """Build MongoDB query from filter parameters."""
        query = {}
        
        if self.category:
            query["category"] = self.category.value
            
        if self.equip_position:
            query["equip_position"] = self.equip_position.value
            
        if self.min_rarity or self.max_rarity:
            rarity_filter = {}
            if self.min_rarity:
                rarity_filter["$gte"] = self.min_rarity.value
            if self.max_rarity:
                rarity_filter["$lte"] = self.max_rarity.value
            query["rarity_tier"] = rarity_filter
            
        if self.required_skill:
            query[f"skill_requirements.{self.required_skill}"] = {"$exists": True}
            if self.max_skill_level:
                query[f"skill_requirements.{self.required_skill}"] = {"$lte": self.max_skill_level}
                
        if self.has_boost:
            query["boost_effects.boost_type"] = self.has_boost.value
            
        if self.tradeable_only is not None:
            query["tradeable"] = self.tradeable_only
            
        if self.equipment_only:
            query["equip_position"] = {"$ne": None}
            
        if self.consumable_only:
            query["category"] = {"$in": ["consumable", "food", "boost_vial"]}
            
        return query


class AssetStatsSummary(BaseModel):
    """Summary statistics for assets."""
    total_assets: int = Field(..., description="Total number of assets")
    by_category: Dict[str, int] = Field(default_factory=dict, description="Count by category")
    by_rarity: Dict[str, int] = Field(default_factory=dict, description="Count by rarity")
    by_equip_position: Dict[str, int] = Field(default_factory=dict, description="Count by equipment position")
    equipment_count: int = Field(default=0, description="Total equipable items")
    consumable_count: int = Field(default=0, description="Total consumable items")
    material_count: int = Field(default=0, description="Total material items")
    with_boosts: int = Field(default=0, description="Items with boost effects")
    tradeable_count: int = Field(default=0, description="Tradeable items")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Stats update time")


# Response models for API endpoints
class EnhancedAssetResponse(BaseModel):
    """API response model for enhanced assets."""
    id: str
    asset_id: Optional[str]
    item_id: Optional[int]
    name: str
    description: Optional[str]
    category: str
    equip_position: Optional[str]
    rarity_tier: str
    skill_requirements: Dict[str, int]
    boost_effects: List[Dict[str, Any]]
    combat_stats: Dict[str, int]
    compatible_skills: List[str]
    required_level: Optional[int]
    tradeable: bool
    display_stats: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_asset(cls, asset: EstForAsset) -> "EnhancedAssetResponse":
        """Create response from EstForAsset model."""
        return cls(
            id=asset.id,
            asset_id=asset.asset_id,
            item_id=asset.item_id,
            name=asset.name,
            description=asset.description,
            category=asset.category.value,
            equip_position=asset.equip_position.name if asset.equip_position else None,
            rarity_tier=asset.rarity_tier.name,
            skill_requirements=asset.skill_requirements,
            boost_effects=[
                {
                    "boost_type": boost.boost_type.name,
                    "value": boost.value,
                    "duration": boost.duration
                }
                for boost in asset.boost_effects
            ],
            combat_stats=asset.combat_stats,
            compatible_skills=asset.compatible_skills,
            required_level=asset.required_level,
            tradeable=asset.tradeable,
            display_stats=asset.get_display_stats(),
            created_at=asset.created_at,
            updated_at=asset.updated_at
        )