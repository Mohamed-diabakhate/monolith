# EstFor Kingdom Definitions Integration

This document describes how the EstFor Kingdom TypeScript/AssemblyScript definitions are integrated into the Python FastAPI application.

## Overview

The `estfor-definitions/` directory contains the official EstFor Kingdom game constants, enums, and type definitions. These are originally written in TypeScript for use in the game's smart contracts and web interfaces. We've created a Python integration that automatically generates equivalent Python constants and enums from these TypeScript definitions.

## Generated Python Module

The integration creates `app/game_constants.py` containing:

- **20 Enums**: Including `Skill`, `EquipPosition`, `BoostType`, `CombatStyle`, `ActivityType`, etc.
- **86 Classes**: Data structures like `Attire` for equipment configurations
- **2,400+ Constants**: Item IDs, equipment constants, and game values

## Usage Examples

### 1. Working with Skills

```python
from app.game_constants import Skill

# Check skill values
mining_skill = Skill.MINING  # Value: 8
combat_skill = Skill.MELEE   # Value: 2

# Iterate through skills
for skill in Skill:
    if skill != Skill.NONE and not skill.name.startswith("RESERVED"):
        print(f"{skill.name}: {skill.value}")
```

### 2. Equipment Management

```python
from app.game_constants import EquipPosition, BRONZE_HELMET, IRON_HELMET

# Define item with equipment position
item = {
    "id": BRONZE_HELMET,  # Value: 1
    "position": EquipPosition.HEAD,  # Value: 1
    "name": "Bronze Helmet"
}

# Check if item can be equipped in slot
def can_equip_in_slot(item_position: EquipPosition, slot: EquipPosition) -> bool:
    if item_position == EquipPosition.BOTH_HANDS:
        return slot in [EquipPosition.LEFT_HAND, EquipPosition.RIGHT_HAND]
    return item_position == slot
```

### 3. Boost Effects

```python
from app.game_constants import BoostType, Skill

def boost_applies_to_skill(boost: BoostType, skill: Skill) -> bool:
    if boost == BoostType.ANY_XP:
        return skill != Skill.NONE
    elif boost == BoostType.COMBAT_XP:
        return skill in [Skill.MELEE, Skill.RANGED, Skill.MAGIC]
    elif boost == BoostType.NON_COMBAT_XP:
        return skill not in [Skill.MELEE, Skill.RANGED, Skill.MAGIC, Skill.DEFENCE]
    return False
```

### 4. Activity Tracking

```python
from app.game_constants import ActivityType

# Categorize activities
clan_activities = [
    ActivityType.ClanCreatedOnMaker,
    ActivityType.ClanInviteSentOnMaker,
    ActivityType.ClanJoinRequestAcceptedOnMaker,
]

reward_activities = [
    ActivityType.DailyReward,
    ActivityType.WeeklyReward,
    ActivityType.QuestCompleted,
]
```

## API Endpoints

The integration provides several API endpoints for game data:

### Get Items
```bash
# Get all helmets
GET /api/game/items/helmets

# Get specific item
GET /api/game/items/1  # Bronze Helmet
```

### Check Equipment Requirements
```bash
POST /api/game/player/can-equip?item_id=2
{
  "skills": {
    "5": 15  # Defence level 15
  }
}
```

### List Game Data
```bash
# List all skills
GET /api/game/skills

# Filter skills by category
GET /api/game/skills?category=combat

# List boost types
GET /api/game/boost-types

# List equipment slots
GET /api/game/equipment-slots
```

### Calculate Boost Effects
```bash
POST /api/game/boost/calculate-effect?skill=8
{
  "boost_type": 2,  # COMBAT_XP
  "value": 50,
  "duration": 3600
}
```

## Regenerating Constants

When the EstFor definitions are updated:

```bash
# Regenerate Python constants from TypeScript
python scripts/generate_estfor_constants.py

# Run tests to verify
pytest tests/test_game_constants.py -v
```

## Project Structure

```
estfor/
├── estfor-definitions/          # Original TypeScript definitions
│   └── src/
│       ├── types.ts            # Enums and classes
│       ├── constants.ts        # Item IDs and values
│       └── index.ts            # Main export
├── scripts/
│   └── generate_estfor_constants.py  # Conversion script
├── app/
│   ├── game_constants.py      # Generated Python constants
│   ├── models/
│   │   └── game_asset.py      # Pydantic models using constants
│   └── routers/
│       └── game_assets.py     # API endpoints for game data
└── tests/
    ├── test_game_constants.py # Tests for generated constants
    └── test_game_assets_api.py # API endpoint tests
```

## Benefits

1. **Type Safety**: Enums prevent invalid values and provide IDE autocompletion
2. **Consistency**: Single source of truth shared with the game's smart contracts
3. **Maintainability**: Automatic generation ensures Python stays in sync with TypeScript
4. **Documentation**: Self-documenting code with meaningful constant names
5. **Validation**: Built-in validation when parsing API requests

## Testing

The integration includes comprehensive tests:

```bash
# Test generated constants
pytest tests/test_game_constants.py -v

# Test API endpoints
pytest tests/test_game_assets_api.py -v

# Run all tests
make test
```

## Future Enhancements

Potential improvements to the integration:

1. **Automatic Updates**: GitHub Action to regenerate when estfor-definitions updates
2. **Type Hints**: Generate more sophisticated type hints for complex structures
3. **Database Models**: Create MongoDB schemas from the definitions
4. **GraphQL Schema**: Generate GraphQL types from the constants
5. **Admin Interface**: Build an admin UI for managing game constants