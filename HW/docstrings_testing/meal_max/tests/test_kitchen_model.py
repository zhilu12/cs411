from contextlib import contextmanager
import pytest
import sqlite3
import re
from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_meal_by_id,
    get_meal_by_name,
    get_leaderboard,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    """Utility function to normalize whitespace in SQL queries for comparison."""
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    """Fixture to mock the database connection and cursor."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Set default behavior for cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Meal Attribute Validation Tests
#
######################################################

def test_valid_meal_initialization():
    """Test that a Meal with valid attributes initializes correctly."""
    meal = Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED")
    assert meal.price == 10.0
    assert meal.difficulty == "MED"

def test_negative_price_raises_value_error():
    """Test that a negative price raises a ValueError."""
    with pytest.raises(ValueError, match="Price must be a positive value."):
        Meal(id=1, meal="Salad", cuisine="French", price=-5.0, difficulty="LOW")

def test_invalid_difficulty_raises_value_error():
    """Test that an invalid difficulty level raises a ValueError."""
    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'."):
        Meal(id=1, meal="Burger", cuisine="American", price=8.0, difficulty="EASY")

######################################################
#
#    Meal Creation Tests
#
######################################################

def test_create_meal_success(mock_cursor):
    """Test creating a new meal successfully."""
    create_meal("Manti", "Turkish", 12.99, "MED")
    expected_query = normalize_whitespace("INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query

    expected_args = ("Manti", "Turkish", 12.99, "MED")
    actual_args = mock_cursor.execute.call_args[0][1]
    assert actual_args == expected_args

def test_create_meal_invalid_price():
    """Test that creating a meal with invalid price raises ValueError."""
    with pytest.raises(ValueError, match="Invalid price: -5.0. Price must be a positive number."):
        create_meal("Pizza", "Italian", -5.0, "LOW")

def test_create_meal_invalid_difficulty():
    """Test that creating a meal with invalid difficulty raises ValueError."""
    with pytest.raises(ValueError, match="Invalid difficulty level: EXTREME. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal("Burger", "American", 10.0, "EXTREME")

def test_create_duplicate_meal(mock_cursor):
    """Test that creating a duplicate meal raises an IntegrityError."""
    mock_cursor.execute.side_effect = sqlite3.IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Manti' already exists"):
        create_meal("Manti", "Turkish", 12.99, "MED")

######################################################
#
#    Clear Meals Test
#
######################################################

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the meals table successfully."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="CREATE TABLE SQL"))
    clear_meals()
    mock_open.assert_called_once_with("sql/create_meal_table.sql", "r")
    mock_cursor.executescript.assert_called_once()

######################################################
#
#    Meal Retrieval Tests
#
######################################################

def test_get_meal_by_id_success(mock_cursor):
    """Test retrieving a meal by ID successfully."""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", False)
    meal = get_meal_by_id(1)
    assert meal == Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED")

def test_get_meal_by_id_not_found(mock_cursor):
    """Test retrieving a non-existent meal by ID raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_deleted(mock_cursor):
    """Test retrieving a deleted meal by ID raises ValueError."""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", True)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        get_meal_by_id(1)

def test_get_meal_by_name_success(mock_cursor):
    """Test retrieving a meal by name successfully."""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", False)
    meal = get_meal_by_name("Pasta")
    assert meal == Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED")

def test_get_meal_by_name_not_found(mock_cursor):
    """Test retrieving a non-existent meal by name raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name Pizza not found"):
        get_meal_by_name("Pizza")

def test_get_meal_by_name_deleted(mock_cursor):
    """Test retrieving a deleted meal by name raises ValueError."""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", True)
    with pytest.raises(ValueError, match="Meal with name Pasta has been deleted"):
        get_meal_by_name("Pasta")

######################################################
#
#    Meal Deletion Tests
#
######################################################

def test_delete_meal_success(mock_cursor):
    """Test deleting a meal by ID successfully."""
    mock_cursor.fetchone.return_value = (False,)
    delete_meal(1)
    assert "UPDATE meals SET deleted = TRUE" in mock_cursor.execute.call_args_list[-1][0][0]

def test_delete_meal_not_found(mock_cursor):
    """Test deleting a non-existent meal raises ValueError."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)

def test_delete_meal_already_deleted(mock_cursor):
    """Test deleting an already deleted meal raises ValueError."""
    mock_cursor.fetchone.return_value = (True,)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

######################################################
#
#    Leaderboard and Statistics Tests
#
######################################################

def test_get_leaderboard_sorted_by_wins(mock_cursor):
    """Test retrieving leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 10.0, "MED", 5, 4, 0.8),
        (2, "Sushi", "Japanese", 15.0, "HIGH", 3, 3, 1.0)
    ]
    leaderboard = get_leaderboard(sort_by="wins")
    assert leaderboard[0]["meal"] == "Pasta"
    assert leaderboard[1]["meal"] == "Sushi"

def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test providing an invalid sort parameter raises ValueError."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard(sort_by="invalid_sort")

def test_update_meal_stats_win(mock_cursor):
    """Test updating meal stats for a win."""
    mock_cursor.fetchone.return_value = (False,)
    update_meal_stats(1, "win")
    assert "UPDATE meals SET battles = battles + 1, wins = wins + 1" in mock_cursor.execute.call_args_list[-1][0][0]

def test_update_meal_stats_loss(mock_cursor):
    """Test updating meal stats for a loss."""
    mock_cursor.fetchone.return_value = (False,)
    update_meal_stats(1, "loss")
    assert "UPDATE meals SET battles = battles + 1" in mock_cursor.execute.call_args_list[-1][0][0]

def test_update_meal_stats_invalid_result(mock_cursor):
    """Test providing an invalid result to update_meal_stats raises ValueError."""
    mock_cursor.fetchone.return_value = (False,)
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_meal_stats(1, "invalid")
