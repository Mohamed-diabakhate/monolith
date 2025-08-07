"""
API endpoints for game assets using EstFor Kingdom constants.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.game_constants import (
    Skill,
    EquipPosition,
    BoostType,
    BRONZE_HELMET,
    IRON_HELMET,
    MITHRIL_HELMET,
    ADAMANTINE_HELMET,
    RUNITE_HELMET,
)
from app.models.game_asset import (
    GameItem,
    PlayerSkills,
    PlayerEquipment,
    BoostEffect,
    PlayerActivity,
)

router = APIRouter(prefix="/api/game", tags=["game_assets"])


class ItemDatabase:
    """Mock database of game items."""
    
    @staticmethod
    def get_helmet_items() -> List[GameItem]:
        """Get all helmet items."""
        return [
            GameItem(
                item_id=BRONZE_HELMET,
                name="Bronze Helmet",
                equip_position=EquipPosition.HEAD,
                skill_requirements={Skill.DEFENCE: 1}
            ),
            GameItem(
                item_id=IRON_HELMET,
                name="Iron Helmet",
                equip_position=EquipPosition.HEAD,
                skill_requirements={Skill.DEFENCE: 10}
            ),
            GameItem(
                item_id=MITHRIL_HELMET,
                name="Mithril Helmet",
                equip_position=EquipPosition.HEAD,
                skill_requirements={Skill.DEFENCE: 20}
            ),
            GameItem(
                item_id=ADAMANTINE_HELMET,
                name="Adamantine Helmet",
                equip_position=EquipPosition.HEAD,
                skill_requirements={Skill.DEFENCE: 30}
            ),
            GameItem(
                item_id=RUNITE_HELMET,
                name="Runite Helmet",
                equip_position=EquipPosition.HEAD,
                skill_requirements={Skill.DEFENCE: 40}
            ),
        ]


@router.get("/items/helmets", response_model=List[GameItem])
async def get_helmets():
    """Get all helmet items with their requirements."""
    return ItemDatabase.get_helmet_items()


@router.get("/items/{item_id}", response_model=GameItem)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    helmets = ItemDatabase.get_helmet_items()
    for helmet in helmets:
        if helmet.item_id == item_id:
            return helmet
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@router.post("/player/can-equip")
async def check_can_equip(
    player_skills: PlayerSkills,
    item_id: int
):
    """Check if a player can equip an item based on skill requirements."""
    helmets = ItemDatabase.get_helmet_items()
    item = None
    for helmet in helmets:
        if helmet.item_id == item_id:
            item = helmet
            break
    
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    
    can_equip = player_skills.can_perform_action(item.skill_requirements or {})
    
    return {
        "item_id": item_id,
        "item_name": item.name,
        "can_equip": can_equip,
        "requirements": item.skill_requirements,
        "player_skills": {
            skill.name: level 
            for skill, level in player_skills.skills.items()
        }
    }


@router.get("/skills", response_model=List[dict])
async def list_skills(
    category: Optional[str] = Query(None, description="Filter by category: combat, gathering, crafting")
):
    """List all available skills, optionally filtered by category."""
    all_skills = []
    
    combat_skills = [Skill.MELEE, Skill.RANGED, Skill.MAGIC, Skill.DEFENCE, Skill.HEALTH]
    gathering_skills = [Skill.MINING, Skill.WOODCUTTING, Skill.FISHING, Skill.FARMING, Skill.HUNTING]
    crafting_skills = [Skill.SMITHING, Skill.CRAFTING, Skill.COOKING, Skill.ALCHEMY, 
                       Skill.FLETCHING, Skill.FORGING]
    
    if category == "combat":
        skills_to_show = combat_skills
    elif category == "gathering":
        skills_to_show = gathering_skills
    elif category == "crafting":
        skills_to_show = crafting_skills
    else:
        skills_to_show = list(Skill)
    
    for skill in skills_to_show:
        if skill != Skill.NONE and not skill.name.startswith("RESERVED"):
            all_skills.append({
                "id": skill.value,
                "name": skill.name,
                "display_name": skill.name.replace("_", " ").title()
            })
    
    return all_skills


@router.get("/boost-types", response_model=List[dict])
async def list_boost_types():
    """List all available boost types and their effects."""
    boost_info = []
    
    boost_descriptions = {
        BoostType.NONE: "No boost effect",
        BoostType.ANY_XP: "Increases XP gain for all skills",
        BoostType.COMBAT_XP: "Increases XP gain for combat skills",
        BoostType.NON_COMBAT_XP: "Increases XP gain for non-combat skills",
        BoostType.GATHERING: "Increases gathering efficiency",
        BoostType.ABSENCE: "Reduces penalty for being away",
        BoostType.PASSIVE_SKIP_CHANCE: "Chance to skip passive requirements",
        BoostType.PVP_BLOCK: "Increases PvP block chance",
        BoostType.PVP_REATTACK: "Allows PvP counter-attacks",
        BoostType.PVP_SUPER_ATTACK: "Enables super attacks in PvP",
        BoostType.COMBAT_FIXED: "Fixed combat stat boost",
    }
    
    for boost_type in BoostType:
        boost_info.append({
            "id": boost_type.value,
            "name": boost_type.name,
            "description": boost_descriptions.get(boost_type, "Unknown effect")
        })
    
    return boost_info


@router.post("/boost/calculate-effect")
async def calculate_boost_effect(
    boost: BoostEffect,
    skill: Skill
):
    """Calculate if a boost applies to a specific skill."""
    applies = boost.applies_to_skill(skill)
    
    return {
        "boost_type": boost.boost_type.name,
        "skill": skill.name,
        "applies": applies,
        "value": boost.value if applies else 0,
        "duration": boost.duration
    }


@router.get("/equipment-slots", response_model=List[dict])
async def list_equipment_slots():
    """List all equipment slots where items can be equipped."""
    slots = []
    
    slot_descriptions = {
        EquipPosition.HEAD: "Helmets and hats",
        EquipPosition.NECK: "Amulets and necklaces",
        EquipPosition.BODY: "Body armor and robes",
        EquipPosition.ARMS: "Gauntlets and bracers",
        EquipPosition.LEGS: "Leg armor and trousers",
        EquipPosition.FEET: "Boots and shoes",
        EquipPosition.RING: "Magical rings",
        EquipPosition.LEFT_HAND: "Weapons and shields",
        EquipPosition.RIGHT_HAND: "Weapons and tools",
        EquipPosition.BOTH_HANDS: "Two-handed weapons",
        EquipPosition.QUIVER: "Arrows and bolts",
        EquipPosition.MAGIC_BAG: "Runes and magical items",
        EquipPosition.FOOD: "Consumable food items",
        EquipPosition.AUX: "Auxiliary items (wood, seeds)",
        EquipPosition.BOOST_VIAL: "Personal boost potions",
    }
    
    for position in EquipPosition:
        if position != EquipPosition.NONE:
            slots.append({
                "id": position.value,
                "name": position.name,
                "description": slot_descriptions.get(position, "Equipment slot")
            })
    
    return slots