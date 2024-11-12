from contextlib import contextmanager
import pytest
import sqlite3
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

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
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
#    Create and Clear Meals
#
######################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""
    create_meal(meal="Pasta", cuisine="Italian", price=15.0, difficulty="MED")

    expected_query = "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)"
    actual_query = mock_cursor.execute.call_args[0][0]
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Pasta", "Italian", 15.0, "MED")
    assert actual_arguments == expected_arguments, f"Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_invalid_price():
    """Test creating a meal with an invalid price (e.g., negative price)."""
    with pytest.raises(ValueError, match="Invalid price: -10.0. Price must be a positive number."):
        create_meal(meal="Soup", cuisine="French", price=-10.0, difficulty="LOW")

def test_create_meal_invalid_difficulty():
    """Test creating a meal with an invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: HARD. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Burger", cuisine="American", price=8.0, difficulty="HARD")

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the meals table."""
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="SQL script"))

    clear_meals()

    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()

######################################################
#
#    Delete Meal
#
######################################################

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog by meal ID."""
    mock_cursor.fetchone.return_value = [False]
    delete_meal(1)

    expected_select_query = "SELECT deleted FROM meals WHERE id = ?"
    expected_update_query = "UPDATE meals SET deleted = TRUE WHERE id = ?"
    
    actual_select_query = mock_cursor.execute.call_args_list[0][0][0]
    actual_update_query = mock_cursor.execute.call_args_list[1][0][0]

    assert actual_select_query == expected_select_query
    assert actual_update_query == expected_update_query

    assert mock_cursor.execute.call_args_list[0][0][1] == (1,)
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_delete_meal_already_deleted(mock_cursor):
    """Test deleting a meal that is already marked as deleted."""
    mock_cursor.fetchone.return_value = [True]
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

def test_delete_meal_not_found(mock_cursor):
    """Test deleting a meal that does not exist."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)

######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by its ID."""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 15.0, "MED", False)
    meal = get_meal_by_id(1)

    expected_meal = Meal(1, "Pasta", "Italian", 15.0, "MED")
    assert meal == expected_meal

    expected_query = "SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?"
    actual_query = mock_cursor.execute.call_args[0][0]
    assert actual_query == expected_query
    assert mock_cursor.execute.call_args[0][1] == (1,)

def test_get_meal_by_id_not_found(mock_cursor):
    """Test retrieving a meal by an invalid ID."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by its name."""
    mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 15.0, "MED", False)
    meal = get_meal_by_name("Pasta")

    expected_meal = Meal(1, "Pasta", "Italian", 15.0, "MED")
    assert meal == expected_meal

    expected_query = "SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?"
    actual_query = mock_cursor.execute.call_args[0][0]
    assert actual_query == expected_query
    assert mock_cursor.execute.call_args[0][1] == ("Pasta",)

def test_get_meal_by_name_not_found(mock_cursor):
    """Test retrieving a meal by an invalid name."""
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name 'Unknown' not found"):
        get_meal_by_name("Unknown")

######################################################
#
#    Leaderboard and Stats
#
######################################################

def test_get_leaderboard(mock_cursor):
    """Test retrieving the leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 15.0, "MED", 10, 7, 0.7),
        (2, "Sushi", "Japanese", 20.0, "HIGH", 5, 4, 0.8)
    ]
    leaderboard = get_leaderboard(sort_by="wins")

    expected_leaderboard = [
        {'id': 1, 'meal': "Pasta", 'cuisine': "Italian", 'price': 15.0, 'difficulty': "MED", 'battles': 10, 'wins': 7, 'win_pct': 70.0},
        {'id': 2, 'meal': "Sushi", 'cuisine': "Japanese", 'price': 20.0, 'difficulty': "HIGH", 'battles': 5, 'wins': 4, 'win_pct': 80.0}
    ]
    assert leaderboard == expected_leaderboard

def test_update_meal_stats_win(mock_cursor):
    """Test updating meal stats with a win."""
    mock_cursor.fetchone.return_value = [False]
    update_meal_stats(1, "win")

    expected_query = "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?"
    actual_query = mock_cursor.execute.call_args_list[1][0][0]
    assert actual_query == expected_query
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)

def test_update_meal_stats_loss(mock_cursor):
    """Test updating meal stats with a loss."""
    mock_cursor.fetchone.return_value = [False]
    update_meal_stats(1, "loss")

    expected_query = "UPDATE meals SET battles = battles + 1 WHERE id = ?"
    actual_query = mock_cursor.execute.call_args_list[1][0][0]
    assert actual_query == expected_query
    assert mock_cursor.execute.call_args_list[1][0][1] == (1,)
