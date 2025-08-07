"""
Asset enrichment service using EstFor Kingdom game constants.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import structlog
from datetime import datetime

from app.game_constants import (
    Skill,
    EquipPosition,
    BoostType,
    # Equipment constants
    BRONZE_HELMET, IRON_HELMET, MITHRIL_HELMET, ADAMANTINE_HELMET, RUNITE_HELMET,
    TITANIUM_HELMET, ORICHALCUM_HELMET, NATUOW_HOOD, BAT_WING_HAT, NATURE_MASK,
    HEAD_BASE, NECK_BASE,
)
from app.models.enhanced_asset import (
    EstForAsset,
    AssetCategory,
    RarityTier,
    EstForBoostEffect,
)

logger = structlog.get_logger()


class AssetEnrichmentService:
    """Service for enriching raw asset data with EstFor game metadata."""
    
    def __init__(self):
        """Initialize the enrichment service with game constants mappings."""
        self._init_item_mappings()
        self._init_category_patterns()
        self._init_skill_mappings()
    
    def _init_item_mappings(self):
        """Initialize item ID to metadata mappings."""
        # Map known item IDs to their metadata
        self.item_metadata = {
            # Helmets
            BRONZE_HELMET: {
                "category": AssetCategory.HELMET,
                "equip_position": EquipPosition.HEAD,
                "skill_requirements": {"DEFENCE": 1},
                "rarity_tier": RarityTier.COMMON,
            },
            IRON_HELMET: {
                "category": AssetCategory.HELMET,
                "equip_position": EquipPosition.HEAD,
                "skill_requirements": {"DEFENCE": 10},
                "rarity_tier": RarityTier.COMMON,
            },
            MITHRIL_HELMET: {
                "category": AssetCategory.HELMET,
                "equip_position": EquipPosition.HEAD,
                "skill_requirements": {"DEFENCE": 20},
                "rarity_tier": RarityTier.UNCOMMON,
            },
            ADAMANTINE_HELMET: {
                "category": AssetCategory.HELMET,
                "equip_position": EquipPosition.HEAD,
                "skill_requirements": {"DEFENCE": 30},
                "rarity_tier": RarityTier.RARE,
            },
            RUNITE_HELMET: {
                "category": AssetCategory.HELMET,
                "equip_position": EquipPosition.HEAD,
                "skill_requirements": {"DEFENCE": 40},
                "rarity_tier": RarityTier.EPIC,
            },
        }
    
    def _init_category_patterns(self):
        """Initialize patterns for detecting asset categories from names."""
        self.category_patterns = {
            AssetCategory.HELMET: [
                r"helmet", r"hat", r"hood", r"cowl", r"mask", r"cap"
            ],
            AssetCategory.ARMOR: [
                r"armor", r"armour", r"body", r"chest", r"plate", r"mail", r"robe"
            ],
            AssetCategory.WEAPON: [
                r"sword", r"axe", r"bow", r"staff", r"wand", r"dagger", r"mace", r"spear"
            ],
            AssetCategory.ACCESSORY: [
                r"ring", r"amulet", r"necklace", r"bracelet", r"cloak", r"cape"
            ],
            AssetCategory.CONSUMABLE: [
                r"potion", r"elixir", r"brew", r"tonic"
            ],
            AssetCategory.BOOST_VIAL: [
                r"vial", r"boost", r"enhancement"
            ],
            AssetCategory.FOOD: [
                r"bread", r"fish", r"meat", r"fruit", r"cake", r"pie", r"stew"
            ],
            AssetCategory.MATERIAL: [
                r"bar", r"ingot", r"essence", r"shard", r"crystal", r"gem"
            ],
            AssetCategory.LOG: [
                r"log", r"wood", r"timber", r"branch"
            ],
            AssetCategory.ORE: [
                r"ore", r"stone", r"rock", r"mineral"
            ],
            AssetCategory.SEED: [
                r"seed", r"seedling", r"sapling"
            ],
            AssetCategory.TOOL: [
                r"pickaxe", r"axe", r"hammer", r"chisel", r"needle", r"saw"
            ],
            AssetCategory.RUNE: [
                r"rune", r"scroll", r"tome", r"spell"
            ],
        }
    
    def _init_skill_mappings(self):
        """Initialize skill name mappings."""
        self.skill_name_map = {
            skill.name.lower(): skill.name for skill in Skill
        }
    
    def enrich_asset(self, raw_asset: Dict[str, Any]) -> EstForAsset:
        """Enrich a raw asset with EstFor game metadata."""
        try:
            # Extract basic fields
            asset_data = {
                "id": str(raw_asset.get("_id", raw_asset.get("id", ""))),
                "asset_id": raw_asset.get("asset_id", raw_asset.get("id")),
                "name": raw_asset.get("name", ""),
                "description": raw_asset.get("description"),
                "type": raw_asset.get("type"),
                "metadata": raw_asset.get("metadata", {}),
                "created_at": raw_asset.get("created_at", datetime.utcnow()),
                "updated_at": raw_asset.get("updated_at", datetime.utcnow()),
            }
            
            # Try to extract item_id from various fields
            item_id = self._extract_item_id(raw_asset)
            if item_id:
                asset_data["item_id"] = item_id
            
            # Enrich with game metadata
            enriched_data = self._enrich_with_game_data(asset_data, raw_asset)
            
            # Create enhanced asset
            enhanced_asset = EstForAsset(**enriched_data)
            
            logger.info("Asset enriched successfully", 
                       asset_id=enhanced_asset.id, 
                       category=enhanced_asset.category.value,
                       item_id=enhanced_asset.item_id)
            
            return enhanced_asset
            
        except Exception as e:
            logger.error("Failed to enrich asset", error=str(e), asset=raw_asset)
            # Return minimal asset on error
            return EstForAsset(
                id=str(raw_asset.get("_id", raw_asset.get("id", "unknown"))),
                name=raw_asset.get("name", "Unknown"),
                description=raw_asset.get("description"),
            )
    
    def _extract_item_id(self, raw_asset: Dict[str, Any]) -> Optional[int]:
        """Extract EstFor item ID from various asset fields."""
        # Try direct item_id field
        if "item_id" in raw_asset and isinstance(raw_asset["item_id"], int):
            return raw_asset["item_id"]
        
        # Try id field if it's an integer
        if "id" in raw_asset and isinstance(raw_asset["id"], int):
            return raw_asset["id"]
        
        # Try extracting from asset_id string
        if "asset_id" in raw_asset:
            asset_id = str(raw_asset["asset_id"])
            # Look for numeric part
            match = re.search(r'\d+', asset_id)
            if match:
                return int(match.group())
        
        # Try extracting from metadata
        metadata = raw_asset.get("metadata", {})
        if "item_id" in metadata:
            try:
                return int(metadata["item_id"])
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _enrich_with_game_data(self, asset_data: Dict[str, Any], raw_asset: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich asset data with game metadata."""
        item_id = asset_data.get("item_id")
        name = asset_data.get("name", "").lower()
        
        # Start with known item metadata if available
        if item_id and item_id in self.item_metadata:
            known_data = self.item_metadata[item_id].copy()
            asset_data.update(known_data)
        else:
            # Infer metadata from name and other fields
            self._infer_category_from_name(asset_data, name)
            self._infer_equip_position(asset_data)
            self._infer_rarity(asset_data, raw_asset)
        
        # Extract skill requirements
        self._extract_skill_requirements(asset_data, raw_asset)
        
        # Extract boost effects
        self._extract_boost_effects(asset_data, raw_asset)
        
        # Extract combat stats
        self._extract_combat_stats(asset_data, raw_asset)
        
        # Determine compatible skills
        self._determine_compatible_skills(asset_data)
        
        # Set other properties
        self._set_additional_properties(asset_data, raw_asset)
        
        return asset_data
    
    def _infer_category_from_name(self, asset_data: Dict[str, Any], name: str):
        """Infer asset category from name patterns."""
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    asset_data["category"] = category
                    return
        
        # Default category
        asset_data["category"] = AssetCategory.UNKNOWN
    
    def _infer_equip_position(self, asset_data: Dict[str, Any]):
        """Infer equipment position from category."""
        category = asset_data.get("category")
        
        if category == AssetCategory.HELMET:
            asset_data["equip_position"] = EquipPosition.HEAD
        elif category == AssetCategory.ARMOR:
            asset_data["equip_position"] = EquipPosition.BODY
        elif category == AssetCategory.WEAPON:
            # Could be left hand, right hand, or both - default to right
            asset_data["equip_position"] = EquipPosition.RIGHT_HAND
        elif category == AssetCategory.ACCESSORY:
            # Could be ring or neck - check name
            name = asset_data.get("name", "").lower()
            if "ring" in name:
                asset_data["equip_position"] = EquipPosition.RING
            elif any(word in name for word in ["amulet", "necklace"]):
                asset_data["equip_position"] = EquipPosition.NECK
    
    def _infer_rarity(self, asset_data: Dict[str, Any], raw_asset: Dict[str, Any]):
        """Infer rarity tier from various sources."""
        # Check metadata for rarity
        metadata = raw_asset.get("metadata", {})
        rarity = metadata.get("rarity", "").lower()
        
        rarity_map = {
            "common": RarityTier.COMMON,
            "uncommon": RarityTier.UNCOMMON,
            "rare": RarityTier.RARE,
            "epic": RarityTier.EPIC,
            "legendary": RarityTier.LEGENDARY,
        }
        
        asset_data["rarity_tier"] = rarity_map.get(rarity, RarityTier.COMMON)
    
    def _extract_skill_requirements(self, asset_data: Dict[str, Any], raw_asset: Dict[str, Any]):
        """Extract skill requirements from asset data."""
        skill_requirements = {}
        
        # Check metadata for skill requirements
        metadata = raw_asset.get("metadata", {})
        requirements = metadata.get("requirements", {})
        
        if isinstance(requirements, dict):
            for skill_name, level in requirements.items():
                # Normalize skill name
                normalized_skill = self._normalize_skill_name(skill_name)
                if normalized_skill:
                    try:
                        skill_requirements[normalized_skill] = int(level)
                    except (ValueError, TypeError):
                        pass
        
        # Infer from category and item name
        category = asset_data.get("category")
        if category in [AssetCategory.HELMET, AssetCategory.ARMOR]:
            # Armor typically requires Defence
            if "DEFENCE" not in skill_requirements:
                skill_requirements["DEFENCE"] = 1
        elif category == AssetCategory.WEAPON:
            # Weapons typically require combat skills
            name = asset_data.get("name", "").lower()
            if any(word in name for word in ["bow", "crossbow"]):
                skill_requirements["RANGED"] = skill_requirements.get("RANGED", 1)
            elif any(word in name for word in ["staff", "wand", "robe"]):
                skill_requirements["MAGIC"] = skill_requirements.get("MAGIC", 1)
            else:
                skill_requirements["MELEE"] = skill_requirements.get("MELEE", 1)
        
        asset_data["skill_requirements"] = skill_requirements
    
    def _normalize_skill_name(self, skill_name: str) -> Optional[str]:
        """Normalize skill name to EstFor constant."""
        normalized = skill_name.upper().replace(" ", "_")
        
        # Direct mapping
        if normalized in [skill.name for skill in Skill]:
            return normalized
        
        # Common variations
        variations = {
            "DEFENSE": "DEFENCE",
            "WC": "WOODCUTTING",
            "MINING": "MINING",
            "FISH": "FISHING",
            "COOK": "COOKING",
            "CRAFT": "CRAFTING",
            "SMITH": "SMITHING",
        }
        
        return variations.get(normalized)
    
    def _extract_boost_effects(self, asset_data: Dict[str, Any], raw_asset: Dict[str, Any]):
        """Extract boost effects from asset data."""
        boost_effects = []
        
        # Check metadata for boosts
        metadata = raw_asset.get("metadata", {})
        boosts = metadata.get("boosts", [])
        
        if isinstance(boosts, list):
            for boost_data in boosts:
                if isinstance(boost_data, dict):
                    try:
                        boost_type_name = boost_data.get("type", "").upper()
                        boost_type = None
                        
                        # Try to match boost type
                        for bt in BoostType:
                            if bt.name == boost_type_name:
                                boost_type = bt
                                break
                        
                        if boost_type:
                            boost_effect = EstForBoostEffect(
                                boost_type=boost_type,
                                value=int(boost_data.get("value", 0)),
                                duration=boost_data.get("duration")
                            )
                            boost_effects.append(boost_effect)
                    except (ValueError, TypeError) as e:
                        logger.warning("Invalid boost data", boost_data=boost_data, error=str(e))
        
        asset_data["boost_effects"] = boost_effects
    
    def _extract_combat_stats(self, asset_data: Dict[str, Any], raw_asset: Dict[str, Any]):
        """Extract combat statistics from asset data."""
        combat_stats = {}
        
        # Check metadata for combat stats
        metadata = raw_asset.get("metadata", {})
        stats = metadata.get("stats", {})
        
        if isinstance(stats, dict):
            stat_mappings = {
                "attack": "attack",
                "defence": "defence",
                "defense": "defence",
                "strength": "strength",
                "magic": "magic",
                "ranged": "ranged",
                "accuracy": "accuracy",
                "damage": "damage",
            }
            
            for stat_key, normalized_key in stat_mappings.items():
                if stat_key in stats:
                    try:
                        combat_stats[normalized_key] = int(stats[stat_key])
                    except (ValueError, TypeError):
                        pass
        
        asset_data["combat_stats"] = combat_stats
    
    def _determine_compatible_skills(self, asset_data: Dict[str, Any]):
        """Determine which skills this item is compatible with."""
        compatible_skills = []
        
        category = asset_data.get("category")
        equip_position = asset_data.get("equip_position")
        
        # Equipment compatibility
        if category in [AssetCategory.HELMET, AssetCategory.ARMOR]:
            compatible_skills.extend(["DEFENCE", "COMBAT"])
        elif category == AssetCategory.WEAPON:
            compatible_skills.extend(["MELEE", "RANGED", "MAGIC", "COMBAT"])
        
        # Tool compatibility
        if category == AssetCategory.TOOL:
            name = asset_data.get("name", "").lower()
            if "pickaxe" in name:
                compatible_skills.append("MINING")
            elif any(word in name for word in ["axe", "saw"]):
                compatible_skills.append("WOODCUTTING")
            elif "hammer" in name:
                compatible_skills.extend(["SMITHING", "FORGING"])
        
        # Material compatibility
        if category in [AssetCategory.MATERIAL, AssetCategory.LOG, AssetCategory.ORE]:
            compatible_skills.extend(["SMITHING", "CRAFTING", "FORGING"])
        
        # Remove duplicates and filter valid skills
        valid_skills = [skill.name for skill in Skill]
        compatible_skills = list(set(skill for skill in compatible_skills if skill in valid_skills))
        
        asset_data["compatible_skills"] = compatible_skills
    
    def _set_additional_properties(self, asset_data: Dict[str, Any], raw_asset: Dict[str, Any]):
        """Set additional asset properties."""
        metadata = raw_asset.get("metadata", {})
        
        # Tradeable (default True unless specified otherwise)
        asset_data["tradeable"] = metadata.get("tradeable", True)
        
        # Required level (infer from skill requirements)
        skill_requirements = asset_data.get("skill_requirements", {})
        if skill_requirements:
            asset_data["required_level"] = max(skill_requirements.values())
    
    def bulk_enrich_assets(self, raw_assets: List[Dict[str, Any]]) -> List[EstForAsset]:
        """Enrich multiple assets in bulk."""
        enriched_assets = []
        
        for raw_asset in raw_assets:
            try:
                enhanced_asset = self.enrich_asset(raw_asset)
                enriched_assets.append(enhanced_asset)
            except Exception as e:
                logger.error("Failed to enrich asset in bulk", error=str(e), asset_id=raw_asset.get("id"))
                # Continue with other assets
        
        logger.info("Bulk asset enrichment completed", 
                   total_requested=len(raw_assets),
                   successfully_enriched=len(enriched_assets))
        
        return enriched_assets


# Global service instance
asset_enrichment_service = AssetEnrichmentService()