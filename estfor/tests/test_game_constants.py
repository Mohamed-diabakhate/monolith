"""
Tests for the generated game constants module.
"""

import pytest
from enum import IntEnum
from dataclasses import is_dataclass

from app.game_constants import (
    BoostType,
    Skill,
    EquipPosition,
    WorldLocation,
    CombatStyle,
    ActionQueueStrategy,
    InstantActionType,
    InstantVRFActionType,
    ActivityType,
    Attire,
    # Constants
    NONE,
    BRONZE_HELMET,
    IRON_HELMET,
    HEAD_BASE,
    NECK_BASE,
)


class TestEnums:
    """Test the generated enum classes."""
    
    def test_boost_type_enum(self):
        """Test BoostType enum values."""
        assert issubclass(BoostType, IntEnum)
        assert BoostType.NONE.value == 0
        assert BoostType.ANY_XP.value == 1
        assert BoostType.COMBAT_XP.value == 2
        assert BoostType.NON_COMBAT_XP.value == 3
        assert BoostType.GATHERING.value == 4
        assert BoostType.COMBAT_FIXED.value == 10
    
    def test_skill_enum(self):
        """Test Skill enum values."""
        assert issubclass(Skill, IntEnum)
        assert Skill.NONE.value == 0
        assert Skill.COMBAT.value == 1
        assert Skill.MELEE.value == 2
        assert Skill.MINING.value == 8
        assert Skill.WOODCUTTING.value == 9
        assert Skill.FISHING.value == 10
        assert Skill.SMITHING.value == 11
        assert Skill.CRAFTING.value == 13
        assert Skill.COOKING.value == 14
        assert Skill.ALCHEMY.value == 17
        assert Skill.TRAVELING.value == 39
        assert Skill.INCUBATION.value == 40
    
    def test_equip_position_enum(self):
        """Test EquipPosition enum values."""
        assert issubclass(EquipPosition, IntEnum)
        assert EquipPosition.NONE.value == 0
        assert EquipPosition.HEAD.value == 1
        assert EquipPosition.NECK.value == 2
        assert EquipPosition.BODY.value == 3
        assert EquipPosition.LEFT_HAND.value == 9
        assert EquipPosition.RIGHT_HAND.value == 10
        assert EquipPosition.BOTH_HANDS.value == 11
        assert EquipPosition.FOOD.value == 14
        assert EquipPosition.BOOST_VIAL.value == 16
        assert EquipPosition.TERRITORY.value == 22
    
    def test_world_location_enum(self):
        """Test WorldLocation enum."""
        assert issubclass(WorldLocation, IntEnum)
        assert WorldLocation.STARTING_AREA.value == 0
    
    def test_combat_style_enum(self):
        """Test CombatStyle enum."""
        assert issubclass(CombatStyle, IntEnum)
        assert CombatStyle.NONE.value == 0
        assert CombatStyle.ATTACK.value == 1
        assert CombatStyle.DEFENCE.value == 2
    
    def test_action_queue_strategy_enum(self):
        """Test ActionQueueStrategy enum."""
        assert issubclass(ActionQueueStrategy, IntEnum)
        assert ActionQueueStrategy.OVERWRITE.value == 0
        assert ActionQueueStrategy.APPEND.value == 1
        assert ActionQueueStrategy.KEEP_LAST_IN_PROGRESS.value == 2
    
    def test_enum_string_representation(self):
        """Test that enums have proper string representation."""
        # IntEnum's str() returns the value as a string
        assert str(Skill.MINING) == "8"
        assert repr(Skill.MINING) == "<Skill.MINING: 8>"
        assert Skill.MINING.name == "MINING"
        assert Skill.MINING.value == 8
    
    def test_enum_comparison(self):
        """Test enum comparison operations."""
        assert Skill.MINING == Skill.MINING
        assert Skill.MINING != Skill.WOODCUTTING
        assert Skill.MINING.value < Skill.WOODCUTTING.value
    
    def test_enum_iteration(self):
        """Test that we can iterate over enum values."""
        skill_values = [s.value for s in Skill]
        assert 0 in skill_values  # NONE
        assert 8 in skill_values  # MINING
        assert 40 in skill_values  # INCUBATION
        assert len(skill_values) > 20  # Should have many skills


class TestConstants:
    """Test the generated constants."""
    
    def test_base_constants(self):
        """Test base constants exist and have correct values."""
        assert NONE == 0
        assert HEAD_BASE == 1
        assert NECK_BASE == 257
    
    def test_helmet_constants(self):
        """Test helmet item constants."""
        assert BRONZE_HELMET == HEAD_BASE
        assert BRONZE_HELMET == 1
        assert IRON_HELMET == HEAD_BASE + 1
        assert IRON_HELMET == 2
    
    def test_constant_types(self):
        """Test that constants are integers."""
        assert isinstance(NONE, int)
        assert isinstance(HEAD_BASE, int)
        assert isinstance(BRONZE_HELMET, int)
        assert isinstance(NECK_BASE, int)


class TestDataClasses:
    """Test the generated dataclasses."""
    
    def test_attire_dataclass(self):
        """Test Attire dataclass structure."""
        assert is_dataclass(Attire)
        
        # Create an instance with default values
        attire = Attire()
        assert attire.head == 0
        assert attire.neck == 0
        assert attire.body == 0
        assert attire.arms == 0
        assert attire.legs == 0
        assert attire.feet == 0
        assert attire.ring == 0
        
        # Create an instance with custom values
        custom_attire = Attire(
            head=BRONZE_HELMET,
            body=100,
            feet=50
        )
        assert custom_attire.head == BRONZE_HELMET
        assert custom_attire.body == 100
        assert custom_attire.feet == 50
        assert custom_attire.neck == 0  # Should still be default
    
    def test_attire_fields(self):
        """Test that Attire has all expected fields."""
        attire = Attire()
        expected_fields = ['head', 'neck', 'body', 'arms', 'legs', 'feet', 'ring']
        for field in expected_fields:
            assert hasattr(attire, field)


class TestIntegration:
    """Integration tests for using constants together."""
    
    def test_skill_and_boost_combination(self):
        """Test combining skills with boost types."""
        # Simulate checking if a boost applies to a skill
        def boost_applies_to_skill(boost_type: BoostType, skill: Skill) -> bool:
            if boost_type == BoostType.COMBAT_XP:
                return skill in [Skill.MELEE, Skill.RANGED, Skill.MAGIC, Skill.DEFENCE]
            elif boost_type == BoostType.NON_COMBAT_XP:
                return skill in [Skill.MINING, Skill.WOODCUTTING, Skill.FISHING, 
                                Skill.SMITHING, Skill.CRAFTING, Skill.COOKING]
            elif boost_type == BoostType.ANY_XP:
                return skill != Skill.NONE
            return False
        
        assert boost_applies_to_skill(BoostType.COMBAT_XP, Skill.MELEE)
        assert not boost_applies_to_skill(BoostType.COMBAT_XP, Skill.MINING)
        assert boost_applies_to_skill(BoostType.NON_COMBAT_XP, Skill.MINING)
        assert boost_applies_to_skill(BoostType.ANY_XP, Skill.MELEE)
        assert boost_applies_to_skill(BoostType.ANY_XP, Skill.MINING)
    
    def test_equipment_positioning(self):
        """Test equipment positioning logic."""
        def can_equip_item(item_position: EquipPosition, slot: EquipPosition) -> bool:
            # Two-handed weapons go in both hands
            if item_position == EquipPosition.BOTH_HANDS:
                return slot in [EquipPosition.LEFT_HAND, EquipPosition.RIGHT_HAND, 
                              EquipPosition.BOTH_HANDS]
            return item_position == slot
        
        assert can_equip_item(EquipPosition.HEAD, EquipPosition.HEAD)
        assert not can_equip_item(EquipPosition.HEAD, EquipPosition.BODY)
        assert can_equip_item(EquipPosition.BOTH_HANDS, EquipPosition.LEFT_HAND)
        assert can_equip_item(EquipPosition.BOTH_HANDS, EquipPosition.RIGHT_HAND)
    
    def test_activity_type_categorization(self):
        """Test categorizing activity types."""
        def is_clan_activity(activity: ActivityType) -> bool:
            clan_activities = [
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
            ]
            return activity in clan_activities
        
        assert is_clan_activity(ActivityType.ClanCreatedOnMaker)
        assert is_clan_activity(ActivityType.ClanInviteSentOnMaker)
        assert not is_clan_activity(ActivityType.Buy)
        assert not is_clan_activity(ActivityType.LevelUp)