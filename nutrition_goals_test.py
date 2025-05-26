import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from google.cloud import bigquery
import data_fetcher

class TestNutritionGoals(unittest.TestCase):
    """Test cases for nutrition goals functionality"""

    @patch("data_fetcher.get_bigquery_client")
    def test_set_user_nutrition_goals(self, mock_get_client):
        """Test setting user nutrition goals successfully"""
        
        """
        AI Prompt:
        Write a unit test named test_set_user_nutrition_goals that verifies the data_fetcher.set_user_nutrition_goals function correctly sets nutrition goals by mocking BigQuery client interactions. Ensure the test mocks a successful database operation, calls the function with test parameters (user_id="test_user", calorie_goal=2000, goal_type="daily"), and verifies that the function returns True upon success.
        """
        
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock query job
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        
        # Set test data
        user_id = "test_user"
        calorie_goal = 2000
        goal_type = "daily"
        
        # Call function
        result = data_fetcher.set_user_nutrition_goals(user_id, calorie_goal, goal_type)
        
        # Assert client was called
        mock_get_client.assert_called_once()
        
        # Assert query was executed
        self.assertTrue(mock_client.query.called)
        
        # Assert result is True
        self.assertTrue(result)

    @patch("data_fetcher.get_bigquery_client")
    def test_set_nutrition_goals_error(self, mock_get_client):
        """Test handling of error when setting nutrition goals"""
        
        """
        AI Prompt:
        Write a unit test named test_set_nutrition_goals_error that verifies data_fetcher.set_user_nutrition_goals properly handles database errors by mocking the BigQuery client to raise an exception. The test should configure the mock to throw an exception when query is called, invoke the function with basic parameters, and assert that the function returns False to indicate the error was caught.
        """
        
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.query.side_effect = Exception("Database error")
        
        # Call function
        result = data_fetcher.set_user_nutrition_goals("user1", 2000)
        
        # Assert result is False
        self.assertFalse(result)

    @patch("data_fetcher.get_bigquery_client")
    def test_get_user_nutrition_goals(self, mock_get_client):
        """Test retrieving user nutrition goals"""
        
        """
        AI Prompt:
        Write a unit test named test_get_user_nutrition_goals that verifies the data_fetcher.get_user_nutrition_goals function correctly retrieves nutrition goals from the database. Mock the BigQuery client to return a sample goal record, call the function with a test user ID, and validate that the returned object contains all expected goal properties with their correct values.
        """
        
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock query job and results
        mock_query_job = MagicMock()
        mock_client.query.return_value = mock_query_job
        
        # Mock row in results
        mock_row = MagicMock()
        mock_row.goal_id = "goal123"
        mock_row.goal_type = "daily"
        mock_row.calorie_target = 2000
        mock_row.start_date = "2023-01-01"
        mock_row.end_date = None
        mock_row.created_at = "2023-01-01 12:00:00"
        
        mock_query_job.result.return_value = [mock_row]
        
        # Set test data
        user_id = "test_user"
        
        # Call function
        result = data_fetcher.get_user_nutrition_goals(user_id)
        
        # Assert client was called
        mock_get_client.assert_called_once()
        
        # Assert query was executed
        self.assertTrue(mock_client.query.called)
        
        # Assert result contains expected data
        self.assertEqual(result["goal_id"], "goal123")
        self.assertEqual(result["goal_type"], "daily")
        self.assertEqual(result["calorie_target"], 2000)
        self.assertEqual(result["start_date"], "2023-01-01")
        self.assertIsNone(result["end_date"])
        self.assertEqual(result["created_at"], "2023-01-01 12:00:00")

    @patch("data_fetcher.get_bigquery_client")
    def test_get_nutrition_goals_not_found(self, mock_get_client):
        """Test when no nutrition goals are found"""
        
        """
        AI Prompt:
        Write a unit test named test_get_nutrition_goals_not_found that verifies the data_fetcher.get_user_nutrition_goals function correctly handles cases where no goals exist for a user. Mock the BigQuery client to return an empty result set, call the function with a non-existent user ID, and verify that the function returns None as expected.
        """
        
        # Setup mock
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock empty result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        
        # Call function
        result = data_fetcher.get_user_nutrition_goals("nonexistent_user")
        
        # Assert result is None
        self.assertIsNone(result)

    @patch("data_fetcher.get_bigquery_client")
    def test_get_nutrition_goals_error(self, mock_get_client):
        """Test handling of error when getting nutrition goals"""
        
        """
        AI Prompt:
        Write a unit test named test_get_nutrition_goals_error that verifies the data_fetcher.get_user_nutrition_goals function properly handles database errors. Mock the BigQuery client to raise an exception when the query method is called, invoke the function with a test user ID, and assert that the function returns None instead of propagating the exception.
        """
        
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.query.side_effect = Exception("Database error")
        
        # Call function
        result = data_fetcher.get_user_nutrition_goals("user1")
        
        # Assert result is None
        self.assertIsNone(result)

    @patch("data_fetcher.get_bigquery_client")
    @patch("data_fetcher.get_user_nutrition_goals")
    def test_get_daily_nutrition_progress(self, mock_get_goals, mock_get_client):
        """Test daily nutrition progress calculation"""
        
        """
        AI Prompt:
        Write a unit test named test_get_daily_nutrition_progress that verifies the data_fetcher.get_daily_nutrition_progress function correctly calculates a user's daily nutrition progress. Mock both the get_user_nutrition_goals function to return predefined goals and the BigQuery client to return consumption data, then verify the function correctly merges this data and calculates accurate progress percentages for the specified date.
        """
        
        # Mock goals data
        mock_goals = {
            "goal_id": "goal123",
            "goal_type": "daily",
            "calorie_target": 2000,
            "start_date": "2023-01-01",
            "end_date": None,
            "created_at": "2023-01-01 12:00:00"
        }
        mock_get_goals.return_value = mock_goals
        
        # Mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock query job and results for progress
        mock_progress_job = MagicMock()
        mock_client.query.return_value = mock_progress_job
        
        # Mock progress row
        mock_progress_row = MagicMock()
        mock_progress_row.progress_id = "progress123"
        mock_progress_row.goal_id = "goal123"
        mock_progress_row.total_calories_consumed = 1500
        mock_progress_row.calories_remaining = 500
        mock_progress_row.updated_at = datetime.now()
        
        mock_progress_job.result.return_value = [mock_progress_row]
        
        # Set test data
        user_id = "test_user"
        date = "2023-01-15"
        
        # Call function
        result = data_fetcher.get_daily_nutrition_progress(user_id, date)
        
        # Check result structure and values
        self.assertEqual(result["goals"], mock_goals)
        self.assertEqual(result["consumption"]["calories"], 1500)
        self.assertEqual(result["remaining"]["calories"], 500)
        self.assertEqual(result["progress"]["calories_percent"], 75.0)  # 1500/2000 * 100

    @patch("data_fetcher.get_bigquery_client")
    @patch("data_fetcher.get_user_nutrition_goals")
    def test_weekly_nutrition_progress(self, mock_get_goals, mock_get_client):
        """Test weekly nutrition progress calculation"""
        
        """
        AI Prompt:
        Write a unit test named test_weekly_nutrition_progress that verifies the data_fetcher.get_weekly_nutrition_progress function correctly aggregates multiple days of nutrition data. Mock the necessary dependencies to return predefined goal and progress data for two days, then verify the function correctly calculates daily averages, overall progress percentages, and structures the result as expected.
        """
        
        # Mock current goal
        mock_goals = {
            "goal_id": "goal123",
            "goal_type": "daily",
            "calorie_target": 2000
        }
        mock_get_goals.return_value = mock_goals
        
        # Mock the BigQuery client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Create mock date objects that support strftime
        date1 = datetime(2023, 1, 1).date()
        date2 = datetime(2023, 1, 2).date()
        
        # Create mock GoalProgress results from database
        mock_row1 = MagicMock()
        mock_row1.date = date1  # Use the actual date object
        mock_row1.goal_id = "goal123"
        mock_row1.total_calories_consumed = 1800
        mock_row1.calories_remaining = 200
        mock_row1.updated_at = datetime(2023, 1, 1, 23, 59, 59)
        
        mock_row2 = MagicMock()
        mock_row2.date = date2  # Use the actual date object
        mock_row2.goal_id = "goal123"
        mock_row2.total_calories_consumed = 1600
        mock_row2.calories_remaining = 400
        mock_row2.updated_at = datetime(2023, 1, 2, 23, 59, 59)
        
        # Mock query job results
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [mock_row1, mock_row2]
        mock_client.query.return_value = mock_query_job
        
        # Create a patch to mock datetime.now to return a fixed date
        with patch('data_fetcher.datetime') as mock_datetime:
            # Configure mocked datetime
            mock_date = datetime(2023, 1, 2, 12, 0, 0)
            mock_datetime.now.return_value = mock_date
            # Make sure date operations work correctly
            mock_datetime.strptime.side_effect = datetime.strptime
            mock_datetime.timedelta = timedelta
            
            # Call function with a specified number of days
            result = data_fetcher.get_weekly_nutrition_progress("user1", days=2)
            
            # Verify the result
            self.assertIsNotNone(result, "Weekly progress result should not be None")
            
            # Check the structure of the result
            self.assertIn("daily_progress", result)
            self.assertIn("averages", result)
            self.assertIn("current_goal", result)
            
            # Verify the averages
            self.assertEqual(result["averages"]["calories"], 1700.0)  # (1800 + 1600) / 2
            self.assertEqual(result["averages"]["calories_remaining"], 300.0)  # (200 + 400) / 2
            
            # Check the progress percentage
            self.assertEqual(result["progress"]["calories_percent"], 85.0)  # (1700 / 2000) * 100

if __name__ == "__main__":
    unittest.main() 