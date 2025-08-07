"""
Game asset models using EstFor Kingdom constants.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.game_constants import (
    Skill,
    EquipPosition,
    BoostType,
    CombatStyle,
    ActivityType,
    Attire,
)


class GameItem(BaseModel):
    """Represents an in-game item."""
    item_id: int = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Item name")
    equip_position: Optional[EquipPosition] = Field(None, description="Where the item can be equipped")
    skill_requirements: Optional[dict[Skill, int]] = Field(None, description="Required skill levels")
    
    @validator('equip_position', pre=True)
    def validate_equip_position(cls, v):
        """Validate equipment position."""
        if v is not None and isinstance(v, int):
            try:
                return EquipPosition(v)
            except ValueError:
                raise ValueError(f"Invalid equipment position: {v}")
        return v


class PlayerSkills(BaseModel):
    """Player skill levels."""
    skills: dict[Skill, int] = Field(default_factory=dict, description="Skill levels")
    
    def get_skill_level(self, skill: Skill) -> int:
        """Get the level for a specific skill."""
        return self.skills.get(skill, 0)
    
    def can_perform_action(self, required_skills: dict[Skill, int]) -> bool:
        """Check if player meets skill requirements."""
        for skill, required_level in required_skills.items():
            if self.get_skill_level(skill) < required_level:
                return False
        return True
    
    def get_combat_level(self) -> int:
        """Calculate overall combat level."""
        combat_skills = [
            Skill.MELEE,
            Skill.RANGED,
            Skill.MAGIC,
            Skill.DEFENCE,
            Skill.HEALTH
        ]
        total = sum(self.get_skill_level(skill) for skill in combat_skills)
        return total // len(combat_skills)


class PlayerEquipment(BaseModel):
    """Player's equipped items."""
    attire: Attire = Field(default_factory=Attire, description="Equipped items")
    
    def equip_item(self, item: GameItem) -> bool:
        """Equip an item if possible."""
        if item.equip_position is None:
            return False
            
        if item.equip_position == EquipPosition.HEAD:
            self.attire.head = item.item_id
        elif item.equip_position == EquipPosition.NECK:
            self.attire.neck = item.item_id
        elif item.equip_position == EquipPosition.BODY:
            self.attire.body = item.item_id
        elif item.equip_position == EquipPosition.ARMS:
            self.attire.arms = item.item_id
        elif item.equip_position == EquipPosition.LEGS:
            self.attire.legs = item.item_id
        elif item.equip_position == EquipPosition.FEET:
            self.attire.feet = item.item_id
        elif item.equip_position == EquipPosition.RING:
            self.attire.ring = item.item_id
        else:
            return False
        return True


class BoostEffect(BaseModel):
    """Represents a boost effect."""
    boost_type: BoostType = Field(..., description="Type of boost")
    value: int = Field(..., description="Boost value (percentage or fixed)")
    duration: int = Field(..., description="Duration in seconds")
    
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


class PlayerActivity(BaseModel):
    """Represents a player activity log entry."""
    player_id: str = Field(..., description="Player identifier")
    activity_type: ActivityType = Field(..., description="Type of activity")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the activity occurred")
    details: dict = Field(default_factory=dict, description="Activity-specific details")
    
    @validator('activity_type', pre=True)
    def validate_activity_type(cls, v):
        """Validate activity type."""
        if isinstance(v, int):
            try:
                return ActivityType(v)
            except ValueError:
                raise ValueError(f"Invalid activity type: {v}")
        return v
    
    def is_clan_activity(self) -> bool:
        """Check if this is a clan-related activity."""
        clan_activities = {
            ActivityType.ClanCreatedOnMaker,
            ActivityType.ClanRankUpdatedOnMaker,
            ActivityType.ClanInviteSentOnMaker,
            ActivityType.ClanJoinRequestSentOnMaker,
            ActivityType.ClanJoinRequestAcceptedOnMaker,
            ActivityType.ClanOwnershipTransferredOnMaker,
            ActivityType.ClanEditedOnMaker,
            ActivityType.ClanUpgradedOnMaker,
            ActivityType.ClanMemberLeftOnMaker,
            ActivityType.ClanKickedOnMaker,
        }
        return self.activity_type in clan_activities
    
    def is_reward_activity(self) -> bool:
        """Check if this is a reward-related activity."""
        reward_activities = {
            ActivityType.DailyReward,
            ActivityType.WeeklyReward,
            ActivityType.XPThresholdReward,
            ActivityType.PendingRandomRewardsClaimed,
            ActivityType.QuestCompleted,
        }
        return self.activity_type in reward_activities


class CombatAction(BaseModel):
    """Represents a combat action."""
    skill: Skill = Field(..., description="Combat skill used")
    style: CombatStyle = Field(..., description="Combat style")
    damage: int = Field(0, description="Damage dealt")
    
    @validator('skill')
    def validate_combat_skill(cls, v):
        """Ensure the skill is a combat skill."""
        valid_combat_skills = {Skill.MELEE, Skill.RANGED, Skill.MAGIC}
        if v not in valid_combat_skills:
            raise ValueError(f"Invalid combat skill: {v}")
        return v