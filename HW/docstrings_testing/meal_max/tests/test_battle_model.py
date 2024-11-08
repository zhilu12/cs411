import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 100, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 200, 'MED')

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


##################################################
# Add Meal Management Test Cases
##################################################

def test_add_meal_to_battle(battle_model, sample_meal1):
    """Test adding a meal to the combatants list."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_add_duplicate_meal_to_combatant_list(battle_model, sample_meal1):
    """Test error when adding a duplicate meal to the battle by ID."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Meal with ID 1 already exists in the battle"):
        battle_model.prep_combatant(sample_meal1)

def test_add_none_combatant(battle_model):
    """Test that adding None as a combatant raises a ValueError."""
    with pytest.raises(ValueError, match="Combatant cannot be None"):
        battle_model.prep_combatant(None)

##################################################
# Remove Meal Management Test Cases
##################################################

def test_clear_meals(battle_model, sample_battle):
    """Test clearning all meals from the combatants list"""
    battle_model.combatants.extend(sample_battle), 
    assert len(battle_model.combatants) == 2

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, f"Expected 0 meal, but got {len(battle_model.combatants)}"

def test_clear_combatants_empty_battle(battle_model):
    """Test clearing the entire combatants list when it's empty."""
    assert len(battle_model.combatants) == 0, "Combatants should be empty before clearing"

    # Call clear_combatants and verify no exceptions are raised and the list is still empty
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Expected combatants list to remain empty after clearing"

##################################################
# Battle Score Management Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test getting battle score of a meal"""
    # Set expected score
    difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}
    expected_score = (sample_meal1.price * len(sample_meal1.cuisine)) - difficulty_modifier[sample_meal1.difficulty]
    score = battle_model.get_battle_score(sample_meal1)
    assert score == expected_score

def test_get_battle_score_with_none(battle_model):
    """Test that get_battle_score raises an error if combatant is None."""
    with pytest.raises(ValueError, match="Combatant cannot be None"):
        battle_model.get_battle_score(None)

##################################################
# Battle Execution Test Cases
##################################################
def test_remove_meal_after_battle(battle_model, sample_battle):
    """Test removing a meal from the combatants list after battle."""
    battle_model.combatants.extend(sample_battle)
    assert len(battle_model.combatants) == 2

    battle_model.battle()
    assert len(battle_model.combatants) == 1, f"Expected 1 meal, but got {len(battle_model.combatants)}"

def test_battle_with_insufficient_combatants(battle_model, sample_meal1):
    """Test starting battle with only one combatants"""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1

    with pytest.raises(ValueError, match="Not enough combatants for a battle"):
        battle_model.battle()

def test_battle_with_no_combatants(battle_model): # Might not be necessary since we are already checking for one
    """Test starting battle with no combatants"""
    assert len(battle_model.combatants) == 0

    with pytest.raises(ValueError, match="Not enough combatants for a battle"):
        battle_model.battle()

##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving a song from the playlist by track number."""
    battle_model.combatants.extend(sample_battle)

    retrieved_combatants = battle_model.get_combatants()
    assert len(retrieved_combatants) == 2, f"Expected 2 meals, but got {len(battle_model.combatants)}"

    # Checking for meal 1
    assert retrieved_combatants[0].id == 1
    assert retrieved_combatants[0].meal == 'Meal 1'
    assert retrieved_combatants[0].cuisine == 'Cuisine 1'
    assert retrieved_combatants[0].price == 100
    assert retrieved_combatants[0].difficulty == 'LOW'

    # Checking for meal 2
    assert retrieved_combatants[1].id == 2
    assert retrieved_combatants[1].meal == 'Meal 2'
    assert retrieved_combatants[1].cuisine == 'Cuisine 2'
    assert retrieved_combatants[1].price == 200
    assert retrieved_combatants[1].difficulty == 'MED'