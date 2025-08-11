# EstFor Kingdom Game Integration Guide

This guide explains how to work with EstFor Kingdom game integration features, including game constants, asset enrichment, and gameplay mechanics.

## Overview

The EstFor Asset Collection System includes deep integration with EstFor Kingdom game mechanics through:

- **Auto-generated Constants**: 2,400+ Python constants from official TypeScript definitions
- **Asset Enrichment**: Transform raw API data into game-aware objects
- **Gameplay Validation**: Equipment compatibility and skill requirement checking
- **Game Logic**: Boost calculations, level requirements, and combat mechanics

## EstFor Kingdom Game Constants

### Available Enums

The system includes 20+ game enums covering all aspects of gameplay:

#### Core Game Mechanics
```python
from app.game_constants import (
    Skill, EquipPosition, BoostType, ActivityType, 
    CombatStyle, AttackType, Element, Biome
)

# Skills (24 total)
Skill.COMBAT     # Combat experience
Skill.MELEE      # Melee combat
Skill.RANGED     # Ranged combat  
Skill.MAGIC      # Magic combat
Skill.DEFENCE    # Defence skill
Skill.HEALTH     # Health skill
Skill.SMITHING   # Smithing crafting
Skill.MINING     # Mining gathering
Skill.WOODCUTTING # Woodcutting gathering
Skill.FISHING    # Fishing gathering
# ... 14 more skills

# Equipment Positions (16 total)
EquipPosition.HEAD     # Head slot (helmets)
EquipPosition.NECK     # Neck slot (amulets)
EquipPosition.BODY     # Body slot (armor)
EquipPosition.ARMS     # Arms slot (gloves)
EquipPosition.LEGS     # Legs slot (pants)
EquipPosition.FEET     # Feet slot (boots)
EquipPosition.WEAPON   # Weapon slot
EquipPosition.SHIELD   # Shield slot
# ... 8 more positions

# Boost Types (30+ total)
BoostType.COMBAT_XP         # Combat XP bonus
BoostType.NON_COMBAT_XP     # Non-combat XP bonus
BoostType.MELEE_XP          # Melee XP bonus
BoostType.MAGIC_XP          # Magic XP bonus
BoostType.GATHERING_XP      # Gathering XP bonus
BoostType.SKILL_XP          # Skill-specific XP
# ... 25 more boost types
```

#### Item Categories and Constants
```python
from app.game_constants import (
    BRONZE_HELMET, IRON_HELMET, MITHRIL_HELMET,
    BRONZE_SWORD, IRON_SWORD, STEEL_SWORD,
    XP_BOOST_SMALL, XP_BOOST_MEDIUM, XP_BOOST_LARGE
)

# Equipment constants (500+ items)
print(f"Bronze Helmet ID: {BRONZE_HELMET}")  # Output: 1
print(f"Iron Sword ID: {IRON_SWORD}")        # Output: 25
print(f"XP Boost ID: {XP_BOOST_SMALL}")      # Output: 150

# Use in asset enrichment
if asset.item_id == BRONZE_HELMET:
    asset.equip_position = EquipPosition.HEAD
    asset.skill_requirements = {"DEFENCE": 1}
```

### Regenerating Constants

When EstFor Kingdom updates their definitions:

```bash
# Update the estfor-definitions submodule
git submodule update --remote estfor-definitions

# Regenerate Python constants
python scripts/generate_estfor_constants.py

# Validate the generated constants
pytest tests/test_game_constants.py -v

# The script generates:
# - 20+ enums with 500+ values
# - 86 constant classes  
# - 2,400+ individual constants
# - Type-safe IntEnum classes
```

## Asset Enrichment Service

### How Asset Enrichment Works

The enrichment service transforms raw EstFor API data into game-aware objects:

```python
# Raw asset from EstFor API
raw_asset = {
    "id": "bronze_helmet_001",
    "name": "Bronze Helmet",
    "description": "A basic helmet made of bronze. Requires 1 Defence."
}

# After enrichment
enriched_asset = {
    "id": "bronze_helmet_001", 
    "name": "Bronze Helmet",
    "item_id": 1,                    # Mapped to BRONZE_HELMET constant
    "category": "helmet",            # Determined from name pattern
    "equip_position": "HEAD",        # Mapped from category
    "rarity_tier": "COMMON",         # Determined from item ID range
    "skill_requirements": {"DEFENCE": 1},  # Extracted from description
    "boost_effects": [],             # No boosts for this item
    "combat_stats": {"defence": 5},  # Base defence value
    "compatible_skills": ["DEFENCE", "COMBAT"],
    "tradeable": true,
    "display_stats": {               # Pre-computed for UI
        "name": "Bronze Helmet",
        "category": "helmet", 
        "rarity": "COMMON",
        "equip_slot": "HEAD",
        "requirements": {"DEFENCE": 1}
    }
}
```

### Enrichment Categories

#### 1. Equipment Categories
```python
CATEGORY_PATTERNS = {
    'helmet': ['helmet', 'hat', 'hood', 'mask', 'cap'],
    'armor': ['armor', 'body', 'chest', 'tunic', 'robe'],
    'weapon': ['sword', 'bow', 'staff', 'wand', 'axe', 'mace'],
    'gloves': ['gloves', 'gauntlets', 'mitts', 'hands'],
    'boots': ['boots', 'shoes', 'sandals', 'feet'],
    'shield': ['shield', 'buckler', 'defender'],
    'ring': ['ring', 'band'],
    'amulet': ['amulet', 'necklace', 'pendant'],
    'consumable': ['potion', 'food', 'drink', 'elixir'],
    'material': ['bar', 'ore', 'log', 'plank', 'cloth'],
    'tool': ['pickaxe', 'axe', 'fishing', 'net']
}
```

#### 2. Rarity Classification  
```python
RARITY_RANGES = {
    'COMMON': (1, 100),      # Bronze tier equipment
    'UNCOMMON': (101, 200),  # Iron tier equipment  
    'RARE': (201, 300),      # Steel tier equipment
    'EPIC': (301, 400),      # Mithril tier equipment
    'LEGENDARY': (401, 500), # Adamant tier equipment
    'MYTHICAL': (501, 600),  # Special/unique items
}
```

#### 3. Skill Extraction
```python
SKILL_PATTERNS = {
    'DEFENCE': [r'defence (\d+)', r'defense (\d+)', r'(\d+) defence'],
    'MELEE': [r'melee (\d+)', r'(\d+) melee', r'attack (\d+)'],
    'MAGIC': [r'magic (\d+)', r'(\d+) magic', r'spell (\d+)'],
    'RANGED': [r'ranged (\d+)', r'(\d+) ranged', r'bow (\d+)'],
    'SMITHING': [r'smithing (\d+)', r'(\d+) smithing'],
    'MINING': [r'mining (\d+)', r'(\d+) mining'],
    # ... patterns for all 24 skills
}
```

## Game Mechanics Integration

### Equipment Compatibility Checking

```python
# Check if player can equip item
async def can_player_equip_item(player_skills: Dict[str, int], asset: EstForAsset) -> bool:
    """
    Validate if player meets skill requirements for equipment
    """
    for skill_name, required_level in asset.skill_requirements.items():
        player_level = player_skills.get(skill_name, 0)
        if player_level < required_level:
            return False
    return True

# Usage example
player_skills = {
    "DEFENCE": 5,
    "MELEE": 8, 
    "MAGIC": 1
}

bronze_helmet = await get_asset("bronze_helmet_001")
can_equip = await can_player_equip_item(player_skills, bronze_helmet)
# Returns: True (player has Defence 5, needs Defence 1)

mithril_helmet = await get_asset("mithril_helmet_001") 
can_equip = await can_player_equip_item(player_skills, mithril_helmet)
# Returns: False (player has Defence 5, needs Defence 20)
```

### Boost Effect Calculations

```python
# Calculate XP boost effects
def calculate_boost_effect(base_xp: int, boost_effects: List[BoostEffect]) -> int:
    """
    Calculate total XP with boost effects applied
    """
    total_multiplier = 1.0
    
    for boost in boost_effects:
        if boost.boost_type == BoostType.COMBAT_XP:
            total_multiplier += boost.value / 100  # Convert percentage
        elif boost.boost_type == BoostType.SKILL_XP:
            total_multiplier += boost.value / 100
    
    return int(base_xp * total_multiplier)

# Usage example
base_combat_xp = 100
helmet_boosts = [
    BoostEffect(boost_type=BoostType.COMBAT_XP, value=10, duration=3600),  # 10% for 1 hour
    BoostEffect(boost_type=BoostType.MELEE_XP, value=5, duration=1800)     # 5% for 30 min
]

boosted_xp = calculate_boost_effect(base_combat_xp, helmet_boosts)
# Returns: 115 (100 + 10% + 5% = 115 XP)
```

### Combat Statistics

```python
# Calculate effective combat stats
def calculate_combat_stats(equipped_items: List[EstForAsset]) -> Dict[str, int]:
    """
    Sum combat stats from all equipped items
    """
    total_stats = {
        'melee': 0,
        'ranged': 0, 
        'magic': 0,
        'defence': 0,
        'health': 0
    }
    
    for item in equipped_items:
        for stat, value in item.combat_stats.items():
            total_stats[stat] = total_stats.get(stat, 0) + value
    
    return total_stats

# Usage example
equipped_gear = [
    bronze_helmet,    # +5 defence
    iron_armor,      # +15 defence, +10 health
    steel_sword      # +25 melee
]

player_stats = calculate_combat_stats(equipped_gear)
# Returns: {'melee': 25, 'defence': 20, 'health': 10, 'ranged': 0, 'magic': 0}
```

## API Integration Examples

### Equipment Slot Filtering

```python
# Get all head equipment player can use
@router.get("/equipment/compatible/{position}")
async def get_compatible_equipment(
    position: EquipPosition,
    player_skills: Dict[str, int],
    min_level: Optional[int] = None
):
    """
    Get equipment for specific slot that player can use
    """
    filters = AssetFilter(
        equip_position=position,
        max_skill_requirements=player_skills,
        min_level=min_level
    )
    
    assets = await db.list_enhanced_assets(filters)
    compatible_items = []
    
    for asset in assets:
        if await can_player_equip_item(player_skills, asset):
            compatible_items.append(asset)
    
    return compatible_items

# Usage
# GET /equipment/compatible/HEAD?player_skills={"DEFENCE":10,"MELEE":5}
# Returns all helmets the player can equip with Defence 10+
```

### Skill-based Item Recommendations

```python
# Recommend items for skill training
@router.get("/recommendations/skill-training/{skill}")
async def recommend_training_items(
    skill: Skill,
    player_level: int,
    budget: Optional[int] = None
):
    """
    Recommend items that boost specific skill XP
    """
    # Find items with XP boosts for this skill
    boost_filters = AssetFilter(
        has_boosts=True,
        boost_skill=skill,
        max_skill_level=player_level  # Player can equip
    )
    
    items = await db.list_enhanced_assets(boost_filters)
    
    # Sort by boost effectiveness
    recommendations = sorted(
        items,
        key=lambda x: get_skill_boost_value(x, skill),
        reverse=True
    )
    
    if budget:
        # Filter by estimated cost (if trading enabled)
        recommendations = [
            item for item in recommendations 
            if estimate_item_cost(item) <= budget
        ]
    
    return recommendations[:10]  # Top 10 recommendations

# Usage  
# GET /recommendations/skill-training/MELEE?player_level=15&budget=1000
# Returns best melee XP boost items for level 15 player under 1000 gold
```

### Player Build Optimization

```python
# Optimize equipment setup for specific playstyle
@router.post("/optimize/build")
async def optimize_player_build(build_request: BuildOptimizationRequest):
    """
    Optimize equipment setup for player goals
    """
    player_skills = build_request.player_skills
    focus_skills = build_request.focus_skills  # Skills to optimize for
    playstyle = build_request.playstyle        # 'combat', 'gathering', 'crafting'
    
    optimized_build = {
        'equipment': {},
        'total_stats': {},
        'boost_effects': [],
        'skill_requirements_met': True
    }
    
    # For each equipment slot
    for position in EquipPosition:
        if position == EquipPosition.NONE:
            continue
            
        # Find best item for this slot based on focus
        best_item = await find_optimal_item(
            position=position,
            player_skills=player_skills,
            focus_skills=focus_skills,
            playstyle=playstyle
        )
        
        if best_item:
            optimized_build['equipment'][position] = best_item
    
    # Calculate total build effectiveness
    optimized_build['total_stats'] = calculate_build_stats(
        optimized_build['equipment']
    )
    
    return optimized_build

# Usage
build_request = {
    "player_skills": {"DEFENCE": 20, "MELEE": 25, "HEALTH": 15},
    "focus_skills": ["MELEE", "DEFENCE"],  
    "playstyle": "combat"
}
# POST /optimize/build
# Returns optimal combat build for melee/defence focus
```

## Testing Game Integration

### Unit Tests for Game Logic

```python
# tests/test_game_mechanics.py
def test_equipment_compatibility():
    """Test equipment compatibility checking"""
    player_skills = {"DEFENCE": 5, "MELEE": 10}
    
    # Bronze helmet (Defence 1) - should be compatible
    bronze_helmet = create_test_asset(
        name="Bronze Helmet",
        skill_requirements={"DEFENCE": 1}
    )
    assert can_player_equip_item(player_skills, bronze_helmet) == True
    
    # Mithril helmet (Defence 20) - should not be compatible  
    mithril_helmet = create_test_asset(
        name="Mithril Helmet", 
        skill_requirements={"DEFENCE": 20}
    )
    assert can_player_equip_item(player_skills, mithril_helmet) == False

def test_boost_calculations():
    """Test XP boost effect calculations"""
    base_xp = 100
    boosts = [
        BoostEffect(boost_type=BoostType.COMBAT_XP, value=25, duration=3600)
    ]
    
    boosted_xp = calculate_boost_effect(base_xp, boosts)
    assert boosted_xp == 125  # 100 + 25% = 125

def test_asset_enrichment():
    """Test raw asset enrichment process"""
    raw_asset = {
        "name": "Iron Sword",
        "description": "A sturdy iron sword. Requires 10 Melee."
    }
    
    enriched = enrich_asset(raw_asset)
    assert enriched.category == "weapon"
    assert enriched.equip_position == EquipPosition.WEAPON
    assert enriched.skill_requirements == {"MELEE": 10}
    assert enriched.rarity_tier == "UNCOMMON"  # Iron tier
```

### Integration Tests

```python
# tests/test_game_integration.py
async def test_equipment_endpoint():
    """Test equipment filtering by position"""
    # Create test data
    await create_test_assets([
        {"name": "Bronze Helmet", "category": "helmet", "equip_position": "HEAD"},
        {"name": "Iron Helmet", "category": "helmet", "equip_position": "HEAD"},  
        {"name": "Bronze Sword", "category": "weapon", "equip_position": "WEAPON"}
    ])
    
    # Test HEAD equipment endpoint
    response = await client.get("/assets/equipment/HEAD")
    assert response.status_code == 200
    
    items = response.json()
    assert len(items) == 2  # 2 helmets
    assert all(item["equip_position"] == "HEAD" for item in items)

async def test_skill_based_filtering():
    """Test filtering by skill requirements"""
    # Test Defence skill items
    response = await client.get("/assets/by-skill/DEFENCE?max_level=5")
    assert response.status_code == 200
    
    items = response.json()  
    for item in items:
        defence_req = item["skill_requirements"].get("DEFENCE", 0)
        assert defence_req <= 5  # Player can equip all returned items
```

## Performance Considerations

### Caching Game Data

```python
# Cache frequently accessed game constants
@lru_cache(maxsize=1000)
def get_item_metadata(item_id: int) -> Optional[Dict]:
    """Cache item metadata lookups"""
    return ITEM_METADATA.get(item_id)

# Cache enriched assets
async def get_cached_enriched_asset(asset_id: str) -> Optional[EstForAsset]:
    cache_key = f"enriched_asset:{asset_id}"
    cached = await redis.get(cache_key)
    
    if cached:
        return EstForAsset.parse_raw(cached)
    
    # Enrich and cache
    asset = await enrich_and_cache_asset(asset_id)
    await redis.setex(cache_key, 3600, asset.json())  # 1 hour TTL
    return asset
```

### Batch Processing

```python
# Process multiple assets efficiently
async def enrich_assets_batch(raw_assets: List[Dict]) -> List[EstForAsset]:
    """Enrich multiple assets in parallel"""
    tasks = [
        asyncio.create_task(enrich_asset_async(asset))
        for asset in raw_assets
    ]
    
    enriched_assets = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return successful enrichments
    return [
        asset for asset in enriched_assets 
        if isinstance(asset, EstForAsset)
    ]
```

---

This guide covers the core aspects of EstFor Kingdom game integration. For additional technical details, see [TECHNICAL.md](TECHNICAL.md) or the interactive API documentation at http://localhost:8000/docs.