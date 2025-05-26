import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta
from google.cloud import bigquery
import data_fetcher

class TestGetNutritionData(unittest.TestCase):
    """Test cases for the get_nutrition_data function"""

    @patch("data_fetcher.get_bigquery_client")
    def test_successful_fetch(self, mock_get_client):
        """Test that a valid query returns expected nutrition data"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_data that mocks BigQuery client responses to verify successful data retrieval. Mock two rows of nutrition data with specific values, then verify the function correctly transforms these rows into dictionaries with proper date formatting and nutritional values. Also validate that the query is executed with the correct user_id and date range parameters.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create mock result rows
        mock_row1 = MagicMock()
        mock_row1.date = date(2024, 7, 15)
        mock_row1.total_calories = 2100.5
        mock_row1.total_protein = 85.2
        mock_row1.total_carbs = 240.3
        mock_row1.total_fat = 70.1
        mock_row1.total_water_ml = 2500
        
        mock_row2 = MagicMock()
        mock_row2.date = date(2024, 7, 16)
        mock_row2.total_calories = 1950.8
        mock_row2.total_protein = 90.5
        mock_row2.total_carbs = 220.1
        mock_row2.total_fat = 65.4
        mock_row2.total_water_ml = 2800
        
        # Set up the mock query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row1, mock_row2]
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_nutrition_data("user1", days=7)
        
        # Verify the results
        self.assertEqual(len(result), 2)
        
        # Check first row values
        self.assertEqual(result[0]["date"], "2024-07-15")
        self.assertEqual(result[0]["total_calories"], 2100.5)
        self.assertEqual(result[0]["total_protein"], 85.2)
        self.assertEqual(result[0]["total_carbs"], 240.3)
        self.assertEqual(result[0]["total_fat"], 70.1)
        self.assertEqual(result[0]["total_water_ml"], 2500)
        
        # Check second row values
        self.assertEqual(result[1]["date"], "2024-07-16")
        self.assertEqual(result[1]["total_calories"], 1950.8)
        self.assertEqual(result[1]["total_protein"], 90.5)
        self.assertEqual(result[1]["total_carbs"], 220.1)
        self.assertEqual(result[1]["total_fat"], 65.4)
        self.assertEqual(result[1]["total_water_ml"], 2800)
        
        # Verify the query was called with correct parameters
        mock_client.query.assert_called_once()
        # Extract job_config from the call
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        
        # Check that parameters list has correct length
        self.assertEqual(len(job_config.query_parameters), 3)
        
        # Verify parameter names
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)
        self.assertIn("start_date", param_names)
        self.assertIn("end_date", param_names)

    @patch("data_fetcher.get_bigquery_client")
    def test_no_results(self, mock_get_client):
        """Test that an empty result from BigQuery returns an empty list"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_data that verifies the function returns an empty list when no data is found. Mock the BigQuery client to return an empty result set, call the function with a test user ID and days parameter, and assert that it returns an empty list while still properly executing the query.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up empty query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_nutrition_data("user1", days=7)
        
        # Verify the result is an empty list
        self.assertEqual(result, [])
        
        # Verify the query was still called
        mock_client.query.assert_called_once()

    @patch("data_fetcher.get_bigquery_client")
    def test_query_exception(self, mock_get_client):
        """Test that an exception during query execution is handled gracefully"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_data that verifies the function gracefully handles database query exceptions. Configure the mock BigQuery client to raise an exception when query is called, invoke the function with a user ID, and verify it returns an empty list rather than propagating the exception to the caller.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Make the query raise an exception
        mock_client.query.side_effect = Exception("Query failed")
        
        # Call the function
        result = data_fetcher.get_nutrition_data("user1", days=7)
        
        # Verify the result is an empty list
        self.assertEqual(result, [])
        
        # Verify the query was called
        mock_client.query.assert_called_once()

    @patch("data_fetcher.get_bigquery_client")
    def test_custom_days_parameter(self, mock_get_client):
        """Test that the days parameter correctly affects the date range"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_data that verifies the days parameter properly determines the date range used in the query. Mock the BigQuery client, call the function with a specific days value (60), and then extract and verify that the start_date and end_date query parameters reflect a date range of exactly that many days, with appropriate tolerance for timezone variations.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function with custom days
        test_days = 60
        data_fetcher.get_nutrition_data("user1", days=test_days)
        
        # Extract job_config from the call
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        
        # Get end_date parameter (should be today)
        end_date_param = next(param for param in job_config.query_parameters if param.name == "end_date")
        end_date_value = end_date_param.value
        
        # Get start_date parameter
        start_date_param = next(param for param in job_config.query_parameters if param.name == "start_date")
        start_date_value = start_date_param.value
        
        # Verify the date range matches the days parameter
        expected_date_diff = timedelta(days=test_days)
        actual_date_diff = end_date_value - start_date_value
        
        # Allow 1 day difference due to potential time zone issues during testing
        self.assertLessEqual(abs(actual_date_diff.days - test_days), 1)


class TestGetMealDetails(unittest.TestCase):
    """Test cases for the get_meal_details function"""

    @patch("data_fetcher.get_bigquery_client")
    def test_successful_fetch(self, mock_get_client):
        """Test that a valid query returns expected meal details"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_meal_details that mocks BigQuery client responses to verify successful meal data retrieval. Create mock results with two detailed meal records containing specific nutritional information, call the function with a test user ID, and verify the function correctly transforms the data into dictionaries with all meal properties preserved and ISO-formatted timestamps.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create mock result rows
        meal_time1 = datetime(2024, 7, 15, 8, 30, 0)
        mock_row1 = MagicMock()
        mock_row1.meal_id = "meal1"
        mock_row1.meal_type = "breakfast"
        mock_row1.meal_name = "Morning Oatmeal"
        mock_row1.meal_time = meal_time1
        mock_row1.food_name = "Oatmeal"
        mock_row1.brand_name = "Quaker"
        mock_row1.quantity = 1.5
        mock_row1.total_calories = 150.0
        mock_row1.total_protein_grams = 5.0
        mock_row1.total_carbs_grams = 27.0
        mock_row1.total_fat_grams = 3.0
        
        meal_time2 = datetime(2024, 7, 15, 12, 15, 0)
        mock_row2 = MagicMock()
        mock_row2.meal_id = "meal2"
        mock_row2.meal_type = "lunch"
        mock_row2.meal_name = "Chicken Salad"
        mock_row2.meal_time = meal_time2
        mock_row2.food_name = "Grilled Chicken"
        mock_row2.brand_name = "Organic Farms"
        mock_row2.quantity = 1.0
        mock_row2.total_calories = 200.0
        mock_row2.total_protein_grams = 30.0
        mock_row2.total_carbs_grams = 0.0
        mock_row2.total_fat_grams = 8.0
        
        # Set up the mock query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row1, mock_row2]
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_meal_details("user1", days=7)
        
        # Verify the results
        self.assertEqual(len(result), 2)
        
        # Check first row values
        self.assertEqual(result[0]["meal_id"], "meal1")
        self.assertEqual(result[0]["meal_type"], "breakfast")
        self.assertEqual(result[0]["meal_name"], "Morning Oatmeal")
        self.assertEqual(result[0]["meal_time"], meal_time1.isoformat())
        self.assertEqual(result[0]["food_name"], "Oatmeal")
        self.assertEqual(result[0]["brand_name"], "Quaker")
        self.assertEqual(result[0]["quantity"], 1.5)
        self.assertEqual(result[0]["total_calories"], 150.0)
        self.assertEqual(result[0]["total_protein_grams"], 5.0)
        self.assertEqual(result[0]["total_carbs_grams"], 27.0)
        self.assertEqual(result[0]["total_fat_grams"], 3.0)
        
        # Check second row values
        self.assertEqual(result[1]["meal_id"], "meal2")
        self.assertEqual(result[1]["meal_type"], "lunch")
        self.assertEqual(result[1]["meal_name"], "Chicken Salad")
        self.assertEqual(result[1]["meal_time"], meal_time2.isoformat())
        self.assertEqual(result[1]["food_name"], "Grilled Chicken")
        self.assertEqual(result[1]["brand_name"], "Organic Farms")
        self.assertEqual(result[1]["quantity"], 1.0)
        self.assertEqual(result[1]["total_calories"], 200.0)
        self.assertEqual(result[1]["total_protein_grams"], 30.0)
        self.assertEqual(result[1]["total_carbs_grams"], 0.0)
        self.assertEqual(result[1]["total_fat_grams"], 8.0)
        
        # Verify the query was called with correct parameters
        mock_client.query.assert_called_once()
        # Extract job_config from the call
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        
        # Check that parameters list has correct length
        self.assertEqual(len(job_config.query_parameters), 3)
        
        # Verify parameter names
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)
        self.assertIn("start_date", param_names)
        self.assertIn("end_date", param_names)

    @patch("data_fetcher.get_bigquery_client")
    def test_no_results(self, mock_get_client):
        """Test that an empty result from BigQuery returns an empty list"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_meal_details that verifies the function returns an empty list when no meal data is found. Mock the BigQuery client to return an empty result set, call the function with a test user ID and days parameter, and assert that the function properly returns an empty list while still executing the query.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up empty query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_meal_details("user1", days=7)
        
        # Verify the result is an empty list
        self.assertEqual(result, [])
        
        # Verify the query was still called
        mock_client.query.assert_called_once()

    @patch("data_fetcher.get_bigquery_client")
    def test_query_exception(self, mock_get_client):
        """Test that an exception during query execution is handled gracefully"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_meal_details that verifies the function gracefully handles database exceptions. Mock the BigQuery client to raise an exception when the query method is called, call the function with a user ID, and verify it returns an empty list rather than propagating the exception.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Make the query raise an exception
        mock_client.query.side_effect = Exception("Query failed")
        
        # Call the function
        result = data_fetcher.get_meal_details("user1", days=7)
        
        # Verify the result is an empty list
        self.assertEqual(result, [])
        
        # Verify the query was called
        mock_client.query.assert_called_once()


class TestGetNutritionPerformanceCorrelation(unittest.TestCase):
    """Test cases for the get_nutrition_performance_correlation function"""

    @patch("data_fetcher.get_nutrition_data")
    @patch("data_fetcher.get_performance_metrics")
    def test_successful_correlation(self, mock_get_performance, mock_get_nutrition):
        """Test that nutritional and performance data are correctly correlated by date"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_performance_correlation that verifies the function properly combines nutrition and workout data by date. Mock both data sources with overlapping and non-overlapping dates, call the function, and verify it creates a date-indexed dictionary that correctly maps nutrition and performance data while handling dates that only appear in one dataset.
        """
        
        # Mock the nutrition data
        mock_get_nutrition.return_value = [
            {
                'date': '2024-07-15',
                'total_calories': 2100.5,
                'total_protein': 85.2,
                'total_carbs': 240.3,
                'total_fat': 70.1,
                'total_water_ml': 2500
            },
            {
                'date': '2024-07-16',
                'total_calories': 1950.8,
                'total_protein': 90.5,
                'total_carbs': 220.1,
                'total_fat': 65.4,
                'total_water_ml': 2800
            }
        ]
        
        # Mock the performance data
        mock_get_performance.return_value = [
            {
                'workout_id': 'workout1',
                'date': '2024-07-15',
                'distance': 5.2,
                'steps': 8500,
                'calories_burned': 450
            },
            {
                'workout_id': 'workout2',
                'date': '2024-07-17',  # Note: different date from nutrition
                'distance': 3.8,
                'steps': 6200,
                'calories_burned': 320
            }
        ]
        
        # Call the function
        result = data_fetcher.get_nutrition_performance_correlation("user1", days=7)
        
        # Verify the results
        self.assertEqual(len(result), 3)  # Should have 3 dates in total
        
        # Check the date with both nutrition and performance data
        self.assertIn('2024-07-15', result)
        self.assertIsNotNone(result['2024-07-15']['nutrition'])
        self.assertIsNotNone(result['2024-07-15']['performance'])
        self.assertEqual(result['2024-07-15']['nutrition']['total_calories'], 2100.5)
        self.assertEqual(result['2024-07-15']['performance']['calories_burned'], 450)
        
        # Check the date with only nutrition data
        self.assertIn('2024-07-16', result)
        self.assertIsNotNone(result['2024-07-16']['nutrition'])
        self.assertIsNone(result['2024-07-16']['performance'])
        self.assertEqual(result['2024-07-16']['nutrition']['total_protein'], 90.5)
        
        # Check the date with only performance data
        self.assertIn('2024-07-17', result)
        self.assertIsNone(result['2024-07-17']['nutrition'])
        self.assertIsNotNone(result['2024-07-17']['performance'])
        self.assertEqual(result['2024-07-17']['performance']['distance'], 3.8)
        
        # Verify the underlying functions were called with correct parameters
        mock_get_nutrition.assert_called_once_with("user1", 7)
        mock_get_performance.assert_called_once_with("user1", 7)

    @patch("data_fetcher.get_nutrition_data")
    @patch("data_fetcher.get_performance_metrics")
    def test_no_nutrition_data(self, mock_get_performance, mock_get_nutrition):
        """Test correlation when there is no nutrition data"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_performance_correlation that tests the scenario when nutrition data is empty but performance data exists. Mock get_nutrition_data to return an empty list and get_performance_metrics to return workout data for a specific date, then verify the function creates entries with null nutrition data but valid performance data.
        """
        
        # Mock empty nutrition data
        mock_get_nutrition.return_value = []
        
        # Mock the performance data
        mock_get_performance.return_value = [
            {
                'workout_id': 'workout1',
                'date': '2024-07-15',
                'distance': 5.2,
                'steps': 8500,
                'calories_burned': 450
            }
        ]
        
        # Call the function
        result = data_fetcher.get_nutrition_performance_correlation("user1", days=7)
        
        # Verify the results
        self.assertEqual(len(result), 1)  # Should have 1 date
        
        # Check the date with only performance data
        self.assertIn('2024-07-15', result)
        self.assertIsNone(result['2024-07-15']['nutrition'])
        self.assertIsNotNone(result['2024-07-15']['performance'])
        
        # Verify the underlying functions were called
        mock_get_nutrition.assert_called_once()
        mock_get_performance.assert_called_once()

    @patch("data_fetcher.get_nutrition_data")
    @patch("data_fetcher.get_performance_metrics")
    def test_no_performance_data(self, mock_get_performance, mock_get_nutrition):
        """Test correlation when there is no performance data"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_performance_correlation that tests the scenario when performance data is empty but nutrition data exists. Mock get_performance_metrics to return an empty list and get_nutrition_data to return nutrition data for a specific date, then verify the function creates entries with valid nutrition data but null performance data.
        """
        
        # Mock the nutrition data
        mock_get_nutrition.return_value = [
            {
                'date': '2024-07-15',
                'total_calories': 2100.5,
                'total_protein': 85.2,
                'total_carbs': 240.3,
                'total_fat': 70.1,
                'total_water_ml': 2500
            }
        ]
        
        # Mock empty performance data
        mock_get_performance.return_value = []
        
        # Call the function
        result = data_fetcher.get_nutrition_performance_correlation("user1", days=7)
        
        # Verify the results
        self.assertEqual(len(result), 1)  # Should have 1 date
        
        # Check the date with only nutrition data
        self.assertIn('2024-07-15', result)
        self.assertIsNotNone(result['2024-07-15']['nutrition'])
        self.assertIsNone(result['2024-07-15']['performance'])
        
        # Verify the underlying functions were called
        mock_get_nutrition.assert_called_once()
        mock_get_performance.assert_called_once()

    @patch("data_fetcher.get_nutrition_data")
    @patch("data_fetcher.get_performance_metrics")
    def test_no_data(self, mock_get_performance, mock_get_nutrition):
        """Test correlation when there is no data at all"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_performance_correlation that verifies the function correctly handles the case when both nutrition and performance data are empty. Mock both dependency functions to return empty lists, call the correlation function, and verify it returns an empty dictionary as the result.
        """
        
        # Mock empty data
        mock_get_nutrition.return_value = []
        mock_get_performance.return_value = []
        
        # Call the function
        result = data_fetcher.get_nutrition_performance_correlation("user1", days=7)
        
        # Verify the results
        self.assertEqual(result, {})  # Should be empty dictionary
        
        # Verify the underlying functions were called
        mock_get_nutrition.assert_called_once()
        mock_get_performance.assert_called_once()

    @patch("data_fetcher.get_nutrition_data")
    @patch("data_fetcher.get_performance_metrics")
    def test_custom_days_parameter(self, mock_get_performance, mock_get_nutrition):
        """Test that days parameter is correctly passed to underlying functions"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_nutrition_performance_correlation that ensures the days parameter is properly passed to the underlying data retrieval functions. Mock both dependency functions, call the correlation function with a custom days value (90), and verify that both get_nutrition_data and get_performance_metrics are called with exactly the same days parameter.
        """
        
        # Mock empty data
        mock_get_nutrition.return_value = []
        mock_get_performance.return_value = []
        
        # Call the function with custom days
        custom_days = 90
        data_fetcher.get_nutrition_performance_correlation("user1", days=custom_days)
        
        # Verify the underlying functions were called with correct days parameter
        mock_get_nutrition.assert_called_once_with("user1", custom_days)
        mock_get_performance.assert_called_once_with("user1", custom_days)


class TestGetUserMeals(unittest.TestCase):
    """Test cases for the get_user_meals function"""

    @patch("data_fetcher.get_bigquery_client")
    def test_successful_fetch(self, mock_get_client):
        """Test fetching user meals successfully"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_user_meals that verifies successful meal data retrieval for a specific date. Mock BigQuery client to return two meal records with detailed nutritional information, call the function with a test user ID and specific date, and verify both the query parameters and resulting meal dictionary structure are correct.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create mock result rows
        mock_row1 = MagicMock()
        mock_row1.meal_id = "meal1"
        mock_row1.meal_type = "breakfast"
        mock_row1.meal_name = "Morning Oatmeal"
        mock_row1.meal_time = datetime(2024, 7, 15, 8, 30, 0)
        mock_row1.calories = 300.0
        mock_row1.protein_grams = 10.0
        mock_row1.carbs_grams = 45.0
        mock_row1.fat_grams = 8.0
        
        mock_row2 = MagicMock()
        mock_row2.meal_id = "meal2"
        mock_row2.meal_type = "lunch"
        mock_row2.meal_name = "Chicken Salad"
        mock_row2.meal_time = datetime(2024, 7, 15, 12, 30, 0)
        mock_row2.calories = 450.0
        mock_row2.protein_grams = 35.0
        mock_row2.carbs_grams = 20.0
        mock_row2.fat_grams = 15.0
        
        # Set up the mock query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row1, mock_row2]
        mock_client.query.return_value = mock_query_job
        
        # Call the function with a specific date
        test_date = datetime(2024, 7, 15).date()
        result = data_fetcher.get_user_meals("test_user", test_date)
        
        # Verify the query was called with correct parameters
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        
        # Check query parameters
        param_values = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(param_values["user_id"], "test_user")
        self.assertEqual(param_values["date"], test_date)
        
        # Verify the results
        self.assertEqual(len(result), 2)
        
        # Check first meal
        self.assertEqual(result[0]["meal_id"], "meal1")
        self.assertEqual(result[0]["meal_type"], "breakfast")
        self.assertEqual(result[0]["meal_name"], "Morning Oatmeal")
        self.assertEqual(result[0]["calories"], 300.0)
        self.assertEqual(result[0]["protein_grams"], 10.0)
        self.assertEqual(result[0]["carbs_grams"], 45.0)
        self.assertEqual(result[0]["fat_grams"], 8.0)
        
        # Check second meal
        self.assertEqual(result[1]["meal_id"], "meal2")
        self.assertEqual(result[1]["meal_type"], "lunch")
        self.assertEqual(result[1]["calories"], 450.0)
        
    @patch("data_fetcher.get_bigquery_client")
    def test_no_meals_found(self, mock_get_client):
        """Test case when no meals are found for a user"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_user_meals that verifies the function returns an empty list when no meals are found for a user. Mock the BigQuery client to return an empty result set, call the function with a test user ID, and assert that it returns an empty list.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up the mock query result with no rows
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_user_meals("test_user")
        
        # Verify the result is an empty list
        self.assertEqual(result, [])
        
    @patch("data_fetcher.get_bigquery_client")
    def test_exception_handling(self, mock_get_client):
        """Test exception handling when database query fails"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_user_meals that tests the exception handling when the database query fails. Configure the mock BigQuery client to raise an exception when query is called, call the function with a test user ID, and verify it returns an empty list rather than propagating the exception.
        """
        
        # Mock the BigQuery client to raise an exception
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.query.side_effect = Exception("Database error")
        
        # Call the function
        result = data_fetcher.get_user_meals("test_user")
        
        # Verify the result is an empty list
        self.assertEqual(result, [])


class TestGetAllFoodItems(unittest.TestCase):
    """Test cases for the get_all_food_items function"""

    @patch("data_fetcher.get_bigquery_client")
    def test_successful_fetch(self, mock_get_client):
        """Test that food items are fetched successfully"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_all_food_items that verifies successful food item data retrieval from the database. Mock the BigQuery client to return two food items with complete nutritional profiles, call the function, and verify it correctly transforms the data into dictionaries with all expected properties including computed display names.
        """
        
        # Mock the BigQuery client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create mock result rows
        mock_row1 = MagicMock()
        mock_row1.food_id = "food1"
        mock_row1.food_name = "Apple"
        mock_row1.brand_name = "Organic"
        mock_row1.calories = 95.0
        mock_row1.protein_grams = 0.5
        mock_row1.carbs_grams = 25.0
        mock_row1.fat_grams = 0.3
        
        mock_row2 = MagicMock()
        mock_row2.food_id = "food2"
        mock_row2.food_name = "Chicken Breast"
        mock_row2.brand_name = "Free Range"
        mock_row2.calories = 165.0
        mock_row2.protein_grams = 31.0
        mock_row2.carbs_grams = 0.0
        mock_row2.fat_grams = 3.6
        
        # Set up the mock query result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row1, mock_row2]
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_all_food_items()
        
        # Verify the results
        self.assertEqual(len(result), 2)
        
        # Check first food item
        self.assertEqual(result[0]["food_id"], "food1")
        self.assertEqual(result[0]["food_name"], "Apple")
        self.assertEqual(result[0]["brand_name"], "Organic")
        self.assertEqual(result[0]["display_name"], "Apple (Organic)")
        self.assertEqual(result[0]["calories"], 95.0)
        self.assertEqual(result[0]["protein_grams"], 0.5)
        self.assertEqual(result[0]["carbs_grams"], 25.0)
        self.assertEqual(result[0]["fat_grams"], 0.3)
        
        # Check second food item
        self.assertEqual(result[1]["food_id"], "food2")
        self.assertEqual(result[1]["food_name"], "Chicken Breast")
        self.assertEqual(result[1]["display_name"], "Chicken Breast (Free Range)")
        
        # Verify the query was called with correct parameters
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        
        # Check query parameters
        param_values = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(param_values["limit"], 100)  # Default limit
        
    @patch("data_fetcher.get_bigquery_client")
    def test_no_food_items(self, mock_get_client):
        """Test handling when no food items are found"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_all_food_items that verifies the function returns an empty list when no food items are found in the database. Mock the BigQuery client to return an empty result set, call the function, and verify that it returns an empty list.
        """
        
        # Mock the BigQuery client with empty result
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up empty result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function
        result = data_fetcher.get_all_food_items()
        
        # Verify the result is an empty list
        self.assertEqual(result, [])
        
    @patch("data_fetcher.get_bigquery_client")
    def test_custom_limit(self, mock_get_client):
        """Test that custom limit is respected"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_all_food_items that verifies the custom limit parameter is correctly passed to the database query. Mock the BigQuery client, call the function with a specific limit value (25), and verify through the query parameters that the exact limit value was used in the query.
        """
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Set up query job
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call the function with custom limit
        custom_limit = 25
        data_fetcher.get_all_food_items(limit=custom_limit)
        
        # Verify the limit parameter was passed correctly
        call_args = mock_client.query.call_args
        job_config = call_args[1]["job_config"]
        param_values = {param.name: param.value for param in job_config.query_parameters}
        self.assertEqual(param_values["limit"], custom_limit)
        
    @patch("data_fetcher.get_bigquery_client")
    def test_exception_handling(self, mock_get_client):
        """Test exception handling when query fails"""
        
        """
        AI Prompt:
        Write a unit test for data_fetcher.get_all_food_items that verifies the function gracefully handles database query exceptions. Configure the mock BigQuery client to raise an exception when query is called, call the function, and verify it returns an empty list rather than propagating the exception.
        """
        
        # Mock the BigQuery client to raise an exception
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.query.side_effect = Exception("Database error")
        
        # Call the function
        result = data_fetcher.get_all_food_items()
        
        # Verify the result is an empty list
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main() 