import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from google.cloud import bigquery
import data_fetcher

class TestAddMeal(unittest.TestCase):
    """Test cases for the add_meal function"""

    @patch("data_fetcher.get_bigquery_client")
    @patch("data_fetcher.datetime")
    def test_successful_add(self, mock_datetime, mock_get_client):
        """Test that a meal is added successfully"""
        
        """
        AI Prompt:
        Write a unit test function test_successful_add that verifies the add_meal function successfully creates a meal entry with the correct parameters. The test should mock the BigQuery client and datetime module, validate that the function returns a valid meal ID, and verify that the query was executed with the expected parameters including user_id, meal_type, meal_name, and meal_time.
        """
        
        # Mock datetime to have a consistent timestamp
        mock_now = datetime(2024, 7, 15, 12, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock successful query execution
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        user_id = "user1"
        meal_type = "lunch"
        meal_name = "Healthy Lunch"
        result = data_fetcher.add_meal(user_id, meal_type, meal_name)
        
        # Verify that a meal ID was returned
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("meal_user1_"))
        
        # Verify the query was called with correct parameters
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        
        # Check query parameters
        param_values = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(param_values["user_id"], user_id)
        self.assertEqual(param_values["meal_type"], meal_type)
        self.assertEqual(param_values["meal_name"], meal_name)
        self.assertEqual(param_values["meal_time"], mock_now)

    @patch("data_fetcher.get_bigquery_client")
    def test_default_meal_time(self, mock_get_client):
        """Test that meal_time defaults to current time when not provided"""
        
        """
        AI Prompt:
        Write a unit test function test_default_meal_time that verifies the add_meal function correctly uses the current time as the default when no meal_time parameter is provided. The test should mock the BigQuery client, call add_meal without a meal_time parameter, and verify that the query parameters include a non-null datetime value for the meal_time field.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock successful query execution
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        
        # Call the function without meal_time
        data_fetcher.add_meal("user1", "breakfast", "Morning Breakfast")
        
        # Verify the query was called
        mock_client.query.assert_called_once()
        
        # Extract meal_time from query parameters
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        meal_time_param = next(param for param in job_config.query_parameters if param.name == "meal_time")
        
        # Verify meal_time is a datetime object (not None)
        self.assertIsNotNone(meal_time_param.value)
        self.assertIsInstance(meal_time_param.value, datetime)

    @patch("data_fetcher.get_bigquery_client")
    def test_custom_meal_time(self, mock_get_client):
        """Test that custom meal_time is used when provided"""
        
        """
        AI Prompt:
        Write a unit test function test_custom_meal_time that verifies the add_meal function correctly uses a custom meal_time value when provided as a parameter. The test should mock the BigQuery client, call add_meal with a specific datetime value for meal_time, and verify that the exact same datetime value is passed to the query parameters.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock successful query execution
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        
        # Create a custom meal time with UTC timezone
        custom_time = datetime(2024, 7, 15, 8, 0, 0, tzinfo=timezone.utc)
        
        # Call the function with custom meal_time
        data_fetcher.add_meal("user1", "breakfast", "Morning Breakfast", meal_time=custom_time)
        
        # Verify the query was called
        mock_client.query.assert_called_once()
        
        # Extract meal_time from query parameters
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        meal_time_param = next(param for param in job_config.query_parameters if param.name == "meal_time")
        
        # Verify meal_time is the custom time we provided
        self.assertEqual(meal_time_param.value, custom_time)

    @patch("data_fetcher.get_bigquery_client")
    def test_query_exception(self, mock_get_client):
        """Test that exceptions during query are handled gracefully"""
        
        """
        AI Prompt:
        Write a unit test function test_query_exception that verifies the add_meal function handles database exceptions gracefully by returning None. The test should mock the BigQuery client to raise an exception when the query method is called, call the add_meal function, and verify that the return value is None and the query method was still called.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Make query raise an exception
        mock_client.query.side_effect = Exception("Query failed")
        
        # Call the function
        result = data_fetcher.add_meal("user1", "lunch", "Lunch")
        
        # Verify result is None on error
        self.assertIsNone(result)
        
        # Verify the query was called
        mock_client.query.assert_called_once()


class TestAddFoodToMeal(unittest.TestCase):
    """Test cases for the add_food_to_meal function"""

    @patch("data_fetcher.get_food_item")
    @patch("data_fetcher.bigquery.Client")
    @patch("data_fetcher.update_daily_nutrition_summary")
    @patch("data_fetcher.datetime")
    def test_successful_add(self, mock_datetime, mock_update_summary, mock_client_class, mock_get_food_item):
        """Test successfully adding a food item to a meal"""
        
        """
        AI Prompt:
        Write a unit test function test_successful_add that verifies the add_food_to_meal function successfully adds a food item to a meal with correct nutritional calculations. The test should mock the necessary dependencies including food item data, calculate expected nutritional values based on quantity, verify the query parameters contain correctly calculated values, and confirm the nutrition summary is updated afterward.
        """
        
        # Mock datetime for consistent timestamp
        mock_now = datetime(2024, 7, 15, 12, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        
        # Mock food item data
        mock_food = {
            'food_id': 'food1',
            'food_name': 'Chicken Breast',
            'calories': 165.0,
            'protein_grams': 31.0,
            'carbs_grams': 0.0,
            'fat_grams': 3.6
        }
        mock_get_food_item.return_value = mock_food
        
        # Mock BigQuery client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock successful query
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        meal_id = "meal1"
        food_id = "food1"
        quantity = 2.0
        result = data_fetcher.add_food_to_meal(meal_id, food_id, quantity)
        
        # Verify result is True for success
        self.assertTrue(result)
        
        # Verify food item was retrieved
        mock_get_food_item.assert_called_once_with(food_id)
        
        # Verify query was executed
        mock_client.query.assert_called_once()
        
        # Extract and verify query parameters
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        param_values = {param.name: param.value for param in job_config.query_parameters}
        
        # Check calculated nutrient values based on quantity
        self.assertEqual(param_values["quantity"], quantity)
        self.assertEqual(param_values["total_calories"], mock_food["calories"] * quantity)
        self.assertEqual(param_values["total_protein"], mock_food["protein_grams"] * quantity)
        self.assertEqual(param_values["total_carbs"], mock_food["carbs_grams"] * quantity)
        self.assertEqual(param_values["total_fat"], mock_food["fat_grams"] * quantity)
        
        # Verify daily nutrition summary was updated
        mock_update_summary.assert_called_once_with(meal_id)

    @patch("data_fetcher.get_food_item")
    def test_food_not_found(self, mock_get_food_item):
        """Test handling of non-existent food items"""
        
        """
        AI Prompt:
        Write a unit test function test_food_not_found that verifies the add_food_to_meal function correctly handles the case when a food item cannot be found. The test should mock get_food_item to return None (simulating no food found), call add_food_to_meal with a non-existent food ID, and verify the function returns False without attempting to execute a query.
        """
        
        # Mock get_food_item to return None (food not found)
        mock_get_food_item.return_value = None
        
        # Call the function
        result = data_fetcher.add_food_to_meal("meal1", "nonexistent_food", 1.0)
        
        # Verify result is False for failure
        self.assertFalse(result)
        
        # Verify get_food_item was called
        mock_get_food_item.assert_called_once_with("nonexistent_food")

    @patch("data_fetcher.get_food_item")
    @patch("data_fetcher.bigquery.Client")
    def test_query_exception(self, mock_client_class, mock_get_food_item):
        """Test that exceptions during query are handled gracefully"""
        
        """
        AI Prompt:
        Write a unit test function test_query_exception that verifies the add_food_to_meal function properly handles database exceptions when adding a food item to a meal. The test should mock get_food_item to return valid food data, mock the BigQuery client to raise an exception during query execution, and verify the function returns False while still attempting to run the query.
        """
        
        # Mock food item data
        mock_food = {
            'food_id': 'food1',
            'food_name': 'Chicken Breast',
            'calories': 165.0,
            'protein_grams': 31.0,
            'carbs_grams': 0.0,
            'fat_grams': 3.6
        }
        mock_get_food_item.return_value = mock_food
        
        # Mock BigQuery client to raise exception
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("Query failed")
        mock_client_class.return_value = mock_client
        
        # Call the function
        result = data_fetcher.add_food_to_meal("meal1", "food1", 1.0)
        
        # Verify result is False for failure
        self.assertFalse(result)
        
        # Verify query was attempted
        mock_client.query.assert_called_once()


class TestGetFoodItem(unittest.TestCase):
    """Test cases for the get_food_item function"""

    @patch("data_fetcher.get_bigquery_client")
    def test_successful_fetch(self, mock_get_client):
        """Test successfully fetching a food item"""
        
        """
        AI Prompt:
        Write a unit test function test_successful_fetch that verifies the get_food_item function correctly retrieves and formats food item data. The test should mock the BigQuery client to return a mock row with complete food nutritional data, call get_food_item with a food ID, and verify that all fields from the database are properly mapped to the returned dictionary.
        """
        
        # Mock BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create mock food item row
        mock_row = MagicMock()
        mock_row.food_id = "food1"
        mock_row.food_name = "Banana"
        mock_row.brand_name = "Organic"
        mock_row.serving_size_grams = 118.0
        mock_row.calories = 105.0
        mock_row.protein_grams = 1.3
        mock_row.carbs_grams = 27.0
        mock_row.fat_grams = 0.4
        mock_row.fiber_grams = 3.1
        mock_row.sugar_grams = 14.0
        mock_row.sodium_mg = 1.0
        
        # Mock successful query with result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_food_item("food1")
        
        # Verify the result contains all expected food data
        self.assertIsNotNone(result)
        self.assertEqual(result["food_id"], "food1")
        self.assertEqual(result["food_name"], "Banana")
        self.assertEqual(result["brand_name"], "Organic")
        self.assertEqual(result["serving_size_grams"], 118.0)
        self.assertEqual(result["calories"], 105.0)
        self.assertEqual(result["protein_grams"], 1.3)
        self.assertEqual(result["carbs_grams"], 27.0)
        self.assertEqual(result["fat_grams"], 0.4)
        self.assertEqual(result["fiber_grams"], 3.1)
        self.assertEqual(result["sugar_grams"], 14.0)
        self.assertEqual(result["sodium_mg"], 1.0)
        
        # Verify query was called with correct parameter
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        food_id_param = next(param for param in job_config.query_parameters if param.name == "food_id")
        self.assertEqual(food_id_param.value, "food1")

    @patch("data_fetcher.get_bigquery_client")
    def test_food_not_found(self, mock_get_client):
        """Test handling of non-existent food items"""
        
        """
        AI Prompt:
        Write a unit test function test_food_not_found that verifies the get_food_item function returns None when a food item does not exist in the database. The test should mock the BigQuery client to return an empty result set, call get_food_item with a non-existent food ID, and verify that the function returns None while still attempting to query the database.
        """
        
        # Mock BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock query with empty result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_food_item("nonexistent_food")
        
        # Verify result is None when food not found
        self.assertIsNone(result)
        
        # Verify query was still called
        mock_client.query.assert_called_once()

    @patch("data_fetcher.get_bigquery_client")
    def test_query_exception(self, mock_get_client):
        """Test that exceptions during query are handled gracefully"""
        
        """
        AI Prompt:
        Write a unit test function test_query_exception that verifies the get_food_item function gracefully handles database exceptions by returning None. The test should mock the BigQuery client to raise an exception when query is called, call get_food_item with any food ID, and verify that the function returns None and logs the error while still attempting to execute the query.
        """
        
        # Mock BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Make query raise an exception
        mock_client.query.side_effect = Exception("Query failed")
        
        # Call the function
        result = data_fetcher.get_food_item("food1")
        
        # Verify result is None on error
        self.assertIsNone(result)
        
        # Verify query was attempted
        mock_client.query.assert_called_once()


if __name__ == '__main__':
    unittest.main() 