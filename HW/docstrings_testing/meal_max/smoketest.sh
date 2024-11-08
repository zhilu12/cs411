#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000"

# Function to check if the service is healthy
check_health() {
    echo "Checking service health..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
    if [ "$response" -eq 200 ]; then
        echo "Service is healthy!"
    else
        echo "Service health check failed with status code: $response"
        exit 1
    fi
}

# Test adding a meal
test_add_meal() {
    echo "Testing: Add Meal"
    curl -X POST -H "Content-Type: application/json" -d '{
        "meal": "Pasta",
        "cuisine": "Italian",
        "price": 8.0,
        "difficulty": "LOW"
    }' "$BASE_URL/meals"
    echo -e "\n"
}

# Test retrieving the leaderboard
test_get_leaderboard() {
    echo "Testing: Get Leaderboard"
    curl -X GET "$BASE_URL/leaderboard"
    echo -e "\n"
}

# Test updating meal stats
test_update_meal_stats() {
    echo "Testing: Update Meal Stats"
    curl -X POST -H "Content-Type: application/json" -d '{
        "meal_id": 1,
        "result": "win"
    }' "$BASE_URL/meals/update_stats"
    echo -e "\n"
}

# Test starting a battle between two meals
test_start_battle() {
    echo "Testing: Start Battle"
    curl -X POST -H "Content-Type: application/json" -d '{
        "meal1_id": 1,
        "meal2_id": 2
    }' "$BASE_URL/battle"
    echo -e "\n"
}

# Run all tests
check_health
test_add_meal
test_get_leaderboard
test_update_meal_stats
test_start_battle
