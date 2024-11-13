#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################


# Clearing all meals
clear_all_meals() {
  echo "Clearing the meals table"
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

# Prepare a meal for battle
create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal: $meal"
  curl -s -X POST -H "Content-Type: application/json" -d "{
    \"meal\": \"$meal\",
    \"cuisine\": \"$cuisine\",
    \"price\": $price,
    \"difficulty\": \"$difficulty\"
  }" "$BASE_URL/create-meal" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal '$meal' created successfully."
  else
    echo "Failed to create meal '$meal'."
    exit 1
  fi
}

delete_meal() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

retrieve_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get neal by ID ($meal_id)."
    exit 1
  fi
}

retrieve_meal_by_name() {
  meal_name=$1

  echo "Retrieving meal by name: $meal_name"
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve meal by name ($meal_name)."
    exit 1
  fi
}

##########################################################
#
# Battle Management
#
##########################################################

prep_combatant() {
  meal=$1
  echo "Preparing meal for battle: $meal"
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "{
    \"meal\": \"$meal\"
  }" "$BASE_URL/prep-combatant")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal '$meal' prepared successfully for battle."
  else
    echo "Failed to prepare meal '$meal' for battle."
    exit 1
  fi
}

# Start a battle
start_battle() {
  echo "Starting a battle between the prepared combatants..."
  response=$(curl -s -X GET "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle executed successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to start the battle."
    exit 1
  fi
}

# Clear combatants
clear_combatants() {
  echo "Clearing all combatants from the battle..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

# Retrieve leaderboard
get_leaderboard() {
  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}


##########################################
# Execute Tests
##########################################

# Health checks
check_health
check_db

# Clearing all meals
clear_all_meals

# Create and prepare meals for battle
create_meal "Spaghetti" "Italian" 10.0 "LOW"
create_meal "Tacos" "Mexican" 8.0 "MED"

# Retrieve meals by ID and name
retrieve_meal_by_id 1
retrieve_meal_by_name "Spaghetti"

# Deleting and readding
delete_meal 1
create_meal "Spaghetti" "Italian" 10.0 "LOW"

# Prepare meals as combatants
prep_combatant "Spaghetti"
prep_combatant "Tacos"

# Start a battle between the two meals
start_battle

# Clear combatants after the battle
clear_combatants

# Get the leaderboard after battles
get_leaderboard

echo "All battle model tests passed successfully!"