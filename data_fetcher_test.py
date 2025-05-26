#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, MagicMock , ANY
from datetime import datetime
from google.cloud import bigquery
import data_fetcher
from data_fetcher import get_user_workouts, get_user_profile, get_genai_advice, get_user_sensor_data, get_user_posts, calculate_streak, get_badges
from datetime import datetime, timedelta

# python3 -m unittest data_fetcher_test.py 
# A simple dummy row class to simulate BigQuery rows.
class DummyRow:
    def __init__(self, sensor_type, timestamp, data, units):
        self.sensor_type = sensor_type
        self.timestamp = timestamp
        self.data = data
        self.units = units

class TestGetUserSensorData(unittest.TestCase):
    '''
    Create a comprehensive unit test file for testing the get_user_sensor_data 
    function from a data_fetcher module. The tests should cover all aspects 
    of the BigQuery data fetching functionality
    
    Use unittest.TestCase as the base class
    Name the test class TestGetUserSensorData
    Include a DummyRow helper class to simulate BigQuery results
    Mock all external dependencies using unittest.mock.patch
    '''
    @patch("data_fetcher.bigquery.Client")
    def test_successful_fetch(self, mock_client_class):
        """Test that a valid query returns the expected sensor data list."""
        dummy_timestamp = datetime(2024, 7, 29, 7, 45, 0)
        dummy_rows = [
            DummyRow("sensor1", dummy_timestamp, 120.0, "bpm"),
            DummyRow("sensor2", dummy_timestamp, 3000.0, "steps"),
            DummyRow("sensor3", dummy_timestamp, 36.5, "°C"),
        ]
        
        fake_query_job = MagicMock()
        fake_query_job.result.return_value = dummy_rows
        
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = fake_query_job
        mock_client_class.return_value = mock_client_instance
        
        result = data_fetcher.get_user_sensor_data("user1", "workout1")
        expected = [
            {
                "sensor_type": "sensor1",
                "timestamp": dummy_timestamp.isoformat(),
                "data": 120.0,
                "units": "bpm",
            },
            {
                "sensor_type": "sensor2",
                "timestamp": dummy_timestamp.isoformat(),
                "data": 3000.0,
                "units": "steps",
            },
            {
                "sensor_type": "sensor3",
                "timestamp": dummy_timestamp.isoformat(),
                "data": 36.5,
                "units": "°C",
            },
        ]
        self.assertEqual(result, expected)
        mock_client_instance.query.assert_called_once()

    @patch("data_fetcher.bigquery.Client")
    def test_no_results(self, mock_client_class):
        """Test that an empty result from BigQuery returns an empty list."""
        fake_query_job = MagicMock()
        fake_query_job.result.return_value = []
        
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = fake_query_job
        mock_client_class.return_value = mock_client_instance
        
        result = data_fetcher.get_user_sensor_data("user1", "nonexistent_workout")
        self.assertEqual(result, [])

    @patch("data_fetcher.bigquery.Client")
    def test_unknown_sensor_type(self, mock_client_class):
        """Test that a sensor type not covered by the CASE statement returns 'unknown'."""
        dummy_timestamp = datetime(2024, 7, 29, 8, 0, 0)
        dummy_rows = [
            DummyRow("sensorX", dummy_timestamp, 50.0, "unknown"),
        ]
        fake_query_job = MagicMock()
        fake_query_job.result.return_value = dummy_rows
        
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = fake_query_job
        mock_client_class.return_value = mock_client_instance
        
        result = data_fetcher.get_user_sensor_data("user1", "workout1")
        expected = [
            {
                "sensor_type": "sensorX",
                "timestamp": dummy_timestamp.isoformat(),
                "data": 50.0,
                "units": "unknown",
            },
        ]
        self.assertEqual(result, expected)

    @patch("data_fetcher.bigquery.Client")
    def test_multiple_rows(self, mock_client_class):
        """Test that multiple rows are correctly processed."""
        dummy_timestamp1 = datetime(2024, 7, 29, 7, 45, 0)
        dummy_timestamp2 = datetime(2024, 7, 29, 7, 50, 0)
        dummy_rows = [
            DummyRow("sensor1", dummy_timestamp1, 110.0, "bpm"),
            DummyRow("sensor2", dummy_timestamp1, 2500.0, "steps"),
            DummyRow("sensor3", dummy_timestamp2, 37.0, "°C"),
        ]
        fake_query_job = MagicMock()
        fake_query_job.result.return_value = dummy_rows
        
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = fake_query_job
        mock_client_class.return_value = mock_client_instance
        
        result = data_fetcher.get_user_sensor_data("user1", "workout1")
        expected = [
            {
                "sensor_type": "sensor1",
                "timestamp": dummy_timestamp1.isoformat(),
                "data": 110.0,
                "units": "bpm",
            },
            {
                "sensor_type": "sensor2",
                "timestamp": dummy_timestamp1.isoformat(),
                "data": 2500.0,
                "units": "steps",
            },
            {
                "sensor_type": "sensor3",
                "timestamp": dummy_timestamp2.isoformat(),
                "data": 37.0,
                "units": "°C",
            },
        ]
        self.assertEqual(result, expected)

    @patch("data_fetcher.bigquery.Client")
    def test_query_exception(self, mock_client_class):
        """Test that an exception during the query is propagated."""
        mock_client_instance = MagicMock()
        mock_client_instance.query.side_effect = Exception("Query failed")
        mock_client_class.return_value = mock_client_instance
        
        with self.assertRaises(Exception) as context:
            data_fetcher.get_user_sensor_data("user1", "workout1")
        self.assertIn("Query failed", str(context.exception))

    @patch("data_fetcher.bigquery.Client")
    def test_query_parameters(self, mock_client_class):
        """Test that the correct query parameters are passed to the BigQuery client."""
        dummy_timestamp = datetime(2024, 7, 29, 7, 45, 0)
        dummy_rows = [DummyRow("sensor1", dummy_timestamp, 100.0, "bpm")]
        fake_query_job = MagicMock()
        fake_query_job.result.return_value = dummy_rows
        
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = fake_query_job
        mock_client_class.return_value = mock_client_instance
        
        user_id = "test_user"
        workout_id = "test_workout"
        data_fetcher.get_user_sensor_data(user_id, workout_id)
        
        # Extract the keyword arguments passed to query.
        args, kwargs = mock_client_instance.query.call_args
        self.assertIn("job_config", kwargs)
        job_config = kwargs["job_config"]
        self.assertEqual(len(job_config.query_parameters), 2)
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)
        self.assertIn("workout_id", param_names)



class TestGetUserWorkouts(unittest.TestCase):
    '''
    AI Prompt:
    Create a comprehensive unit test file for testing the get_user_workouts 
    function that fetches workout data from BigQuery. The tests should 
    cover all aspects of the workout data fetching functionality
    
    Use unittest.TestCase as the base class
    Name the test class TestGetUserWorkouts
    Mock all external dependencies using unittest.mock.patch and MagicMock
    Include proper setup for BigQuery client mocking

    '''

    @patch('google.cloud.bigquery.Client')  # Mock the BigQuery client
    def test_successful_fetch(self, MockBigQueryClient):
        mock_client = MagicMock()
        MockBigQueryClient.return_value = mock_client
        
        # Mock the result of the query
        mock_query_result = [
            MagicMock(
                WorkoutId="workout1",
                StartTimestamp="2025-04-05 09:00:00",
                EndTimestamp="2025-04-05 10:00:00",
                StartLocationLat=37.7749,
                StartLocationLong=-122.4194,
                EndLocationLat=37.7849,
                EndLocationLong=-122.4294,
                TotalDistance=5.0,
                TotalSteps=5000,
                CaloriesBurned=300
            )
        ]
        
        mock_client.query.return_value.result.return_value = mock_query_result
        
        # Call the function
        result = get_user_workouts("user1")
        
        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['workout_id'], "workout1")
        self.assertEqual(result[0]['start_lat_lng'], (37.7749, -122.4194))
        self.assertEqual(result[0]['end_lat_lng'], (37.7849, -122.4294))
        self.assertEqual(result[0]['distance'], 5.0)
        self.assertEqual(result[0]['steps'], 5000)
        self.assertEqual(result[0]['calories_burned'], 300)

    @patch('google.cloud.bigquery.Client')
    def test_no_results(self, MockBigQueryClient):
        mock_client = MagicMock()
        MockBigQueryClient.return_value = mock_client
        
        # Mock an empty query result
        mock_client.query.return_value.result.return_value = []

        # Call the function
        result = get_user_workouts("user1")
        
        # Assertions
        self.assertEqual(result, [])

    @patch('google.cloud.bigquery.Client')
    def test_query_parameters(self, mock_client_class):
        """Test that the correct query parameters are passed to the BigQuery client."""
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        # Mock query result
        # Set up the mock query result
        mock_query_result = [
            MagicMock(
                WorkoutId="workout1",
                StartTimestamp=datetime(2025, 4, 5, 9, 0, 0),
                EndTimestamp=datetime(2025, 4, 5, 10, 0, 0),
                StartLocationLat=37.7749,
                StartLocationLong=-122.4194,
                EndLocationLat=37.7849,
                EndLocationLong=-122.4294,
                TotalDistance=5.0,
                TotalSteps=5000,
                CaloriesBurned=300
            )
        ]
        
        # Set up the mock query job
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = mock_query_result
        mock_client_instance.query.return_value = mock_query_job
        
        # Call the function
        get_user_workouts("user1")
        
        # Check that query was called
        mock_client_instance.query.assert_called_once()
        
        # Extract and inspect the job_config
        args, kwargs = mock_client_instance.query.call_args
        job_config = kwargs.get("job_config")
        self.assertIsNotNone(job_config)
        self.assertEqual(len(job_config.query_parameters), 1)
        
        # Check parameter name
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)

        
    @patch('google.cloud.bigquery.Client')
    def test_query_exception(self, MockBigQueryClient):
        mock_client = MagicMock()
        MockBigQueryClient.return_value = mock_client
        
        # Make the query fail
        mock_client.query.side_effect = Exception("Query failed")
        
        with self.assertRaises(Exception):
            get_user_workouts("user1")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_missing_data(self, MockBigQueryClient):
        mock_client = MagicMock()
        MockBigQueryClient.return_value = mock_client
        
        # Mock query result with missing data
        mock_query_result = [
            MagicMock(
                WorkoutId="workout1",
                StartTimestamp="2025-04-05 09:00:00",
                EndTimestamp="2025-04-05 10:00:00",
                StartLocationLat=37.7749,
                StartLocationLong=None,  # Missing longitude
                EndLocationLat=None,     # Missing latitude
                EndLocationLong=None,    # Missing longitude
                TotalDistance=5.0,
                TotalSteps=5000,
                CaloriesBurned=300
            )
        ]
        
        mock_client.query.return_value.result.return_value = mock_query_result
        
        # Call the function
        result = get_user_workouts("user1")
        
        # Assertions for missing data
        self.assertEqual(result[0]['start_lat_lng'], (37.7749, 0))  # Default missing values to 0
        self.assertEqual(result[0]['end_lat_lng'], (0, 0))  # Default missing values to 0
    
    

class TestGetGenAIAdvice(unittest.TestCase):
    
    '''
    AI Prompt:
    Create a comprehensive unit test file for testing the get_genai_advice function
    
    Use unittest.TestCase as the base class
    Name the test class TestGetGenAIAdvice
    Include a helper method _create_mock_workout_row for creating consistent mock workout data
    Mock all external dependencies including:
    BigQuery Client
    Vertex AI initialization
    GenerativeModel
    datetime
    random.choice
    '''
    
    @patch('google.cloud.bigquery.Client')
    @patch('data_fetcher.vertexai')
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.datetime')
    @patch('data_fetcher.random.choice')
    def test_successful_advice_generation(self, mock_random_choice, mock_datetime, 
                                        mock_generative_model, mock_vertexai, mock_client):
        """Test that advice is generated successfully with valid data."""
        # Set up mock for datetime
        mock_datetime.now.return_value.strftime.return_value = '2025-04-06 10:00:00'
        
        # Set up mock for random.choice
        mock_random_choice.return_value = "http://example.com/test_image.jpg"
        
        # Set up mock for BigQuery client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        mock_workout_result = MagicMock()
        mock_workout_rows = [
            self._create_mock_workout_row("workout1", "user1", "2025-04-05 07:00:00", 
                                        "2025-04-05 08:00:00", 37.7749, -122.4194, 
                                        37.8049, -122.421, 5.0, 8000, 400.0,
                                        "sensor1", "2025-04-05 07:15:00", 120.0, 
                                        "Heart Rate", "bpm")
        ]
        mock_workout_result.result.return_value = mock_workout_rows
        
        mock_image_result = MagicMock()
        mock_image_rows = [
            MagicMock(ImageURL="http://example.com/image1.jpg"),
            MagicMock(ImageURL="http://example.com/image2.jpg")
        ]
        mock_image_result.result.return_value = mock_image_rows
        
        # Configure query method to return different results based on query content
        def side_effect_query(query, job_config=None):
            if "Images.ImageURL" in query:
                return mock_image_result
            else:
                return mock_workout_result
                
        mock_client_instance.query.side_effect = side_effect_query
        
        # Set up mock for GenerativeModel
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Increase your running pace by 10% to improve cardiovascular efficiency."
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model
        
        # Call the function
        result = get_genai_advice("user1")
        
        # Verify Vertex AI was initialized
        mock_vertexai.init.assert_called_once_with(
            project="bamboo-creek-450920-h2", 
            location="us-central1"
        )
        
        # Verify GenerativeModel was called with the correct model name
        mock_generative_model.assert_called_once_with("gemini-1.5-flash-002")
        
        # Verify BigQuery queries were executed
        self.assertEqual(mock_client_instance.query.call_count, 2)
        
        # Check that the generate_content method was called
        mock_model.generate_content.assert_called_once()
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn("advice_id", result)
        self.assertIn("timestamp", result)
        self.assertIn("content", result)
        self.assertIn("image", result)
        
        # Check result values
        self.assertEqual(result["timestamp"], '2025-04-06 10:00:00')
        self.assertEqual(result["content"], "Increase your running pace by 10% to improve cardiovascular efficiency.")
        self.assertEqual(result["image"], "http://example.com/test_image.jpg")
    
    @patch('google.cloud.bigquery.Client')
    @patch('data_fetcher.vertexai')
    @patch('data_fetcher.GenerativeModel')
    def test_no_workouts_found(self, mock_generative_model, mock_vertexai, mock_client):
        """Test handling when no workouts are found for the user."""
        # Set up mock for BigQuery client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Set up mock for empty workout results
        mock_workout_result = MagicMock()
        mock_workout_result.result.return_value = []
        
        # Set up mock for image results
        mock_image_result = MagicMock()
        mock_image_result.result.return_value = [
            MagicMock(ImageURL="http://example.com/image1.jpg")
        ]
        
        # Configure query method to return different results based on query content
        def side_effect_query(query, job_config=None):
            if "Images.ImageURL" in query:
                return mock_image_result
            else:
                return mock_workout_result
                
        mock_client_instance.query.side_effect = side_effect_query
        
        # Set up mock for GenerativeModel
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "No workout data available yet. Start with a 20-minute walk today."
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model
        
        # Call the function
        result = get_genai_advice("user_with_no_data")
        
        # Check that the model was still called (should handle empty data)
        mock_model.generate_content.assert_called_once()
        
        # Check that we got advice even without workout data
        self.assertIn("content", result)
        self.assertEqual(result["content"], "No workout data available yet. Start with a 20-minute walk today.")
    
    @patch('google.cloud.bigquery.Client')
    @patch('data_fetcher.vertexai')
    @patch('data_fetcher.GenerativeModel')
    def test_no_images_found(self, mock_generative_model, mock_vertexai, mock_client):
        """Test handling when no images are found in the database."""
        # Set up mock for BigQuery client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        mock_workout_result = MagicMock()
        mock_workout_result.result.return_value = [
            self._create_mock_workout_row("workout1", "user1", "2025-04-05 07:00:00", 
                                        "2025-04-05 08:00:00", 37.7749, -122.4194, 
                                        37.8049, -122.421, 5.0, 8000, 400.0,
                                        "sensor1", "2025-04-05 07:15:00", 120.0, 
                                        "Heart Rate", "bpm")
        ]
        
        mock_image_result = MagicMock()
        mock_image_result.result.return_value = []  # Empty image results
        
        # Configure query method to return different results based on query content
        def side_effect_query(query, job_config=None):
            if "Images.ImageURL" in query:
                return mock_image_result
            else:
                return mock_workout_result
                    
        mock_client_instance.query.side_effect = side_effect_query
        
        # Set up mock for GenerativeModel
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Some advice text"
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model
        
        # Call the function
        result = get_genai_advice("user1")
        
        # Check that we handle empty image results (should choose None from images list)
        self.assertIn("image", result)
        self.assertIsNone(result["image"])
    
    @patch('google.cloud.bigquery.Client')
    @patch('data_fetcher.vertexai')
    @patch('data_fetcher.GenerativeModel')
    def test_error_in_model_response(self, mock_generative_model, mock_vertexai, mock_client):
        """Test handling when the AI model raises an exception."""
        # Set up mock for BigQuery client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        mock_workout_result = MagicMock()
        mock_workout_result.result.return_value = [
            self._create_mock_workout_row("workout1", "user1", "2025-04-05 07:00:00", 
                                        "2025-04-05 08:00:00", 37.7749, -122.4194, 
                                        37.8049, -122.421, 5.0, 8000, 400.0,
                                        "sensor1", "2025-04-05 07:15:00", 120.0, 
                                        "Heart Rate", "bpm")
        ]
        
        mock_image_result = MagicMock()
        mock_image_result.result.return_value = [
            MagicMock(ImageURL="http://example.com/image1.jpg")
        ]
        
        # Configure query method to return different results based on query content
        def side_effect_query(query, job_config=None):
            if "Images.ImageURL" in query:
                return mock_image_result
            else:
                return mock_workout_result
                    
        mock_client_instance.query.side_effect = side_effect_query
        
        # Set up mock for GenerativeModel to raise an exception
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("Model error")
        mock_generative_model.return_value = mock_model
        
        # Test the function with error handling
        with self.assertRaises(Exception):
            result = get_genai_advice("user1")
    
    def _create_mock_workout_row(self, workout_id, user_id, start_time, end_time, 
                                start_lat, start_long, end_lat, end_long, 
                                distance, steps, calories, sensor_id, 
                                sensor_time, sensor_value, sensor_name, units):
        """Helper method to create mock workout data rows."""
        mock_row = MagicMock()
        mock_row.WorkoutId = workout_id
        mock_row.UserId = user_id
        mock_row.StartTimestamp = start_time
        mock_row.EndTimestamp = end_time
        mock_row.StartLocationLat = start_lat
        mock_row.StartLocationLong = start_long
        mock_row.EndLocationLat = end_lat
        mock_row.EndLocationLong = end_long
        mock_row.TotalDistance = distance
        mock_row.TotalSteps = steps
        mock_row.CaloriesBurned = calories
        mock_row.SensorId = sensor_id
        mock_row.Timestamp = sensor_time
        mock_row.SensorValue = sensor_value
        mock_row.Name = sensor_name
        mock_row.Units = units
        return mock_row


'''
AI Prompt:

Create comprehensive unit test files for testing data 
fetching functions get_user_profile and get_user_posts
The implementation should precisely replicate the reference test files
structure and behavior while maintaining all specified test coverage for
user profile and post data fetching.

'''

class TestGetUserProfile(unittest.TestCase):
    @patch("data_fetcher.bigquery.Client")
    def test_successful_fetch(self, mock_client_class):
        """Test that a valid query returns the expected user profile."""
        # Mock data for the user profile
        mock_user_row = MagicMock(
            Name="Test User",
            Username="testuser",
            ImageUrl="http://example.com/image.jpg",
            DateOfBirth=datetime(1990, 1, 1)
        )
        
        # Mock data for the user's friends
        mock_friends_rows = [
            MagicMock(UserId2="friend1"),
            MagicMock(UserId2="friend2")
        ]
        
        # Mock the query job for user profile
        mock_user_query_job = MagicMock()
        mock_user_query_job.result.return_value = [mock_user_row]
        
        # Mock the query job for friends
        mock_friends_query_job = MagicMock()
        mock_friends_query_job.result.return_value = mock_friends_rows
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.side_effect = [mock_user_query_job, mock_friends_query_job]
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        result = get_user_profile("user1")
        
        # Assertions
        self.assertEqual(result["full_name"], "Test User")
        self.assertEqual(result["username"], "testuser")
        self.assertEqual(result["profile_image"], "http://example.com/image.jpg")
        self.assertEqual(result["date_of_birth"], "1990-01-01")
        self.assertEqual(result["friends"], ["friend1", "friend2"])
        
        # Check that query was called twice (once for user, once for friends)
        self.assertEqual(mock_client_instance.query.call_count, 2)

    @patch("data_fetcher.bigquery.Client")
    def test_no_user_found(self, mock_client_class):
        """Test that a ValueError is raised when no user is found."""
        # Mock an empty result for the user query
        mock_user_query_job = MagicMock()
        mock_user_query_job.result.return_value = []
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = mock_user_query_job
        mock_client_class.return_value = mock_client_instance
        
        # Call the function and check for the exception
        with self.assertRaises(ValueError) as context:
            get_user_profile("nonexistent_user")
        self.assertIn("not found in the database", str(context.exception))

    @patch("data_fetcher.bigquery.Client")
    def test_missing_date_of_birth(self, mock_client_class):
        """Test that missing date of birth is handled correctly."""
        # Mock data with a missing date of birth
        mock_user_row = MagicMock(
            Name="Test User",
            Username="testuser",
            ImageUrl="http://example.com/image.jpg",
            DateOfBirth=None
        )
        
        # Mock data for the user's friends
        mock_friends_rows = [
            MagicMock(UserId2="friend1"),
            MagicMock(UserId2="friend2")
        ]
        
        # Mock the query job for user profile
        mock_user_query_job = MagicMock()
        mock_user_query_job.result.return_value = [mock_user_row]
        
        # Mock the query job for friends
        mock_friends_query_job = MagicMock()
        mock_friends_query_job.result.return_value = mock_friends_rows
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.side_effect = [mock_user_query_job, mock_friends_query_job]
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        result = get_user_profile("user1")
        
        # Assertions
        self.assertIsNone(result["date_of_birth"])

    @patch("data_fetcher.bigquery.Client")
    def test_query_parameters(self, mock_client_class):
        """Test that the correct query parameters are passed to the BigQuery client."""
        # Mock data for the user profile
        mock_user_row = MagicMock(
            Name="Test User",
            Username="testuser",
            ImageUrl="http://example.com/image.jpg",
            DateOfBirth=datetime(1990, 1, 1)
        )
        
        # Mock data for the user's friends
        mock_friends_rows = [
            MagicMock(UserId2="friend1"),
            MagicMock(UserId2="friend2")
        ]
        
        # Mock the query job for user profile
        mock_user_query_job = MagicMock()
        mock_user_query_job.result.return_value = [mock_user_row]
        
        # Mock the query job for friends
        mock_friends_query_job = MagicMock()
        mock_friends_query_job.result.return_value = mock_friends_rows
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.side_effect = [mock_user_query_job, mock_friends_query_job]
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        get_user_profile("user1")
        
        # Check that query was called twice (once for user, once for friends)
        self.assertEqual(mock_client_instance.query.call_count, 2)
        
        # Extract and inspect the actual job_config argument for the first query
        _, kwargs = mock_client_instance.query.call_args_list[0]
        job_config = kwargs.get("job_config")
        self.assertIsNotNone(job_config)
        self.assertEqual(len(job_config.query_parameters), 1)
        
        # Check parameter name and value
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)
        
        # Extract and inspect the actual job_config argument for the second query
        _, kwargs = mock_client_instance.query.call_args_list[1]
        job_config = kwargs.get("job_config")
        self.assertIsNotNone(job_config)
        self.assertEqual(len(job_config.query_parameters), 1)
        
        # Check parameter name and value
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)

    @patch("data_fetcher.bigquery.Client")
    def test_query_exception(self, mock_client_class):
        """Test that an exception during the query is propagated."""
        mock_client_instance = MagicMock()
        mock_client_instance.query.side_effect = Exception("Query failed")
        mock_client_class.return_value = mock_client_instance
        
        with self.assertRaises(Exception) as context:
            get_user_profile("user1")
        self.assertIn("Query failed", str(context.exception))

class TestGetUserPosts(unittest.TestCase):
    @patch("data_fetcher.bigquery.Client")
    def test_successful_fetch(self, mock_client_class):
        """Test that a valid query returns the expected list of posts."""
        # Mock data for the posts
        mock_post_rows = [
            MagicMock(
                PostId="post1",
                Timestamp=datetime(2024, 1, 1, 10, 0, 0),
                ImageUrl="http://example.com/post1.jpg",
                Content="Post 1 content"
            ),
            MagicMock(
                PostId="post2",
                Timestamp=datetime(2024, 1, 2, 12, 0, 0),
                ImageUrl=None,
                Content="Post 2 content"
            )
        ]
        
        # Mock the query job
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = mock_post_rows
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        result = get_user_posts("user1")
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["user_id"], "user1")
        self.assertEqual(result[0]["post_id"], "post1")
        self.assertEqual(result[0]["timestamp"], "2024-01-01 10:00:00")
        self.assertEqual(result[0]["content"], "Post 1 content")
        self.assertEqual(result[0]["image"], "http://example.com/post1.jpg")
        self.assertEqual(result[1]["user_id"], "user1")
        self.assertEqual(result[1]["post_id"], "post2")
        self.assertEqual(result[1]["timestamp"], "2024-01-02 12:00:00")
        self.assertEqual(result[1]["content"], "Post 2 content")
        self.assertIsNone(result[1]["image"])

    @patch("data_fetcher.bigquery.Client")
    def test_no_posts_found(self, mock_client_class):
        """Test that an empty list is returned when no posts are found."""
        # Mock an empty result
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        result = get_user_posts("nonexistent_user")
        
        # Assertions
        self.assertEqual(result, [])

    @patch("data_fetcher.bigquery.Client")
    def test_missing_timestamp(self, mock_client_class):
        """Test that missing timestamp is handled correctly."""
        # Mock data with a missing timestamp
        mock_post_rows = [
            MagicMock(
                PostId="post1",
                Timestamp=None,
                ImageUrl="http://example.com/post1.jpg",
                Content="Post 1 content"
            )
        ]
        
        # Mock the query job
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = mock_post_rows
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        result = get_user_posts("user1")
        
        # Assertions
        self.assertIsNone(result[0]["timestamp"])

    @patch("data_fetcher.bigquery.Client")
    def test_query_parameters(self, mock_client_class):
        """Test that the correct query parameters are passed to the BigQuery client."""
        # Mock data for the posts
        mock_post_rows = [
            MagicMock(
                PostId="post1",
                Timestamp=datetime(2024, 1, 1, 10, 0, 0),
                ImageUrl="http://example.com/post1.jpg",
                Content="Post 1 content"
            )
        ]
        
        # Mock the query job
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = mock_post_rows
        
        # Mock the client instance
        mock_client_instance = MagicMock()
        mock_client_instance.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client_instance
        
        # Call the function
        get_user_posts("user1")
        
        # Check that query was called
        mock_client_instance.query.assert_called_once()
        
        # Extract and inspect the actual job_config argument
        _, kwargs = mock_client_instance.query.call_args
        job_config = kwargs.get("job_config")
        self.assertIsNotNone(job_config)
        self.assertEqual(len(job_config.query_parameters), 1)
        
        # Check parameter name and value
        param_names = [param.name for param in job_config.query_parameters]
        self.assertIn("user_id", param_names)

    @patch("data_fetcher.bigquery.Client")
    def test_query_exception(self, mock_client_class):
        """Test that an exception during the query is propagated."""
        mock_client_instance = MagicMock()
        mock_client_instance.query.side_effect = Exception("Query failed")
        mock_client_class.return_value = mock_client_instance
        
        with self.assertRaises(Exception) as context:
            get_user_posts("user1")
        self.assertIn("Query failed", str(context.exception))


class TestStreakLogic(unittest.TestCase):

    def create_workouts(self, days_ago_list):
        """Helper to generate workouts with start_timestamps on specific days ago"""
        today = datetime.now().date()
        return [{
            'start_timestamp': (today - timedelta(days=d)).isoformat()
        } for d in days_ago_list]

    def test_empty_workouts(self):
        workouts = []
        current, longest = calculate_streak(workouts)
        self.assertEqual(current, 0)
        self.assertEqual(longest, 0)

    def test_single_day_workout_today(self):
        workouts = self.create_workouts([0])
        current, longest = calculate_streak(workouts)
        self.assertEqual(current, 1)
        self.assertEqual(longest, 1)

    def test_three_day_streak(self):
        workouts = self.create_workouts([0, 1, 2])
        current, longest = calculate_streak(workouts)
        self.assertEqual(current, 3)
        self.assertEqual(longest, 3)

    def test_streak_broken(self):
        workouts = self.create_workouts([0, 2, 3])
        current, longest = calculate_streak(workouts)
        self.assertEqual(current, 1)  # only today counts
        self.assertEqual(longest, 2)

    def test_old_longest_streak(self):
        workouts = self.create_workouts([0, 1, 2, 10, 11, 12, 13])
        current, longest = calculate_streak(workouts)
        self.assertEqual(current, 3)
        self.assertEqual(longest, 4)

    def test_get_badges(self):
        workouts = self.create_workouts([0, 1, 2, 3, 4, 5, 6])
        current, longest = calculate_streak(workouts)
        badges = get_badges(workouts, current, longest)
        self.assertIn("3-Day Streak", badges)
        self.assertIn("7-Day Streak", badges)
        self.assertNotIn("14-Day Warrior", badges)

    def test_badge_for_50_workouts(self):
        today = datetime.now().date()
        workouts = [{'start_timestamp': (today - timedelta(days=i)).isoformat()} for i in range(50)]
        current, longest = calculate_streak(workouts)
        badges = get_badges(workouts, current, longest)
        self.assertIn("50 Workouts Legend", badges)

if __name__ == '__main__':
    unittest.main()
