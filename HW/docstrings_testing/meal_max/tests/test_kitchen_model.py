import pytest
from meal_max.models.kitchen_model import create_meal, clear_meals, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats
from meal_max.models.kitchen_model import Meal

# Fixtures to provide sample meals for testing
@pytest.fixture
def sample_meal():
    return Meal(id=1, meal="Pizza", cuisine="Italian", price=10.0, difficulty="LOW")

@pytest.fixture
def another_meal():
    return Meal(id=2, meal="Sushi", cuisine="Japanese", price=15.0, difficulty="MED")


# Test case for creating a meal
def test_create_meal(sample_meal):
    """Test that a new meal is created and added to the database."""
    clear_meals()  # Clear existing meals
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    created_meal = get_meal_by_name(sample_meal.meal)
    assert created_meal.meal == sample_meal.meal, "The meal name should match"
    assert created_meal.cuisine == sample_meal.cuisine, "The cuisine type should match"
    assert created_meal.price == sample_meal.price, "The price should match"
    assert created_meal.difficulty == sample_meal.difficulty, "The difficulty level should match"


# Test case for clearing all meals
def test_clear_meals():
    """Test that all meals are cleared from the database."""
    create_meal("Pasta", "Italian", 12.0, "LOW")
    clear_meals()
    with pytest.raises(ValueError):
        get_meal_by_name("Pasta")


# Test case for deleting a meal
def test_delete_meal(sample_meal):
    """Test deleting a meal by ID."""
    clear_meals()
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    delete_meal(sample_meal.id)
    with pytest.raises(ValueError):
        get_meal_by_id(sample_meal.id)


# Test case for retrieving leaderboard
def test_get_leaderboard(sample_meal, another_meal):
    """Test that the leaderboard is correctly retrieved and sorted."""
    clear_meals()
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    create_meal(another_meal.meal, another_meal.cuisine, another_meal.price, another_meal.difficulty)
    update_meal_stats(sample_meal.id, "win")
    leaderboard = get_leaderboard(sort_by="wins")
    assert len(leaderboard) >= 1, "Leaderboard should contain at least one entry"
    assert leaderboard[0]["wins"] >= leaderboard[-1]["wins"], "Leaderboard should be sorted by wins"


# Test case for getting a meal by ID
def test_get_meal_by_id(sample_meal):
    """Test retrieving a meal by its ID."""
    clear_meals()
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    fetched_meal = get_meal_by_id(sample_meal.id)
    assert fetched_meal.meal == sample_meal.meal, "Fetched meal name should match created meal name"


# Test case for getting a meal by name
def test_get_meal_by_name(sample_meal):
    """Test retrieving a meal by its name."""
    clear_meals()
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    fetched_meal = get_meal_by_name(sample_meal.meal)
    assert fetched_meal.meal == sample_meal.meal, "Fetched meal name should match created meal name"


# Test case for updating meal stats
def test_update_meal_stats(sample_meal):
    """Test updating the battle statistics of a meal."""
    clear_meals()
    create_meal(sample_meal.meal, sample_meal.cuisine, sample_meal.price, sample_meal.difficulty)
    update_meal_stats(sample_meal.id, "win")
    updated_meal = get_meal_by_id(sample_meal.id)
    assert updated_meal.wins == 1, "Wins count should be updated to 1"
    assert updated_meal.battles == 1, "Battles count should be updated to 1"
