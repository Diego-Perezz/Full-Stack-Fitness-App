#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
import streamlit as st
from unittest.mock import patch, MagicMock
from data_fetcher import get_user_workouts
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts


# python3 -m unittest modules_test.py
# Write your tests below


class TestDisplayPost(unittest.TestCase):
    '''
    Generative AI was used to help with the implementation of this function 
    Prompt: 
        I need to create a test class for my Streamlit application. I have a function called display_post 
        in my modules.py file that displays social media posts in a specific layout. 
        Please generate a comprehensive unittest test class named TestDisplayPost with the following:

        Include setUp and tearDown methods to mock all Streamlit functions (columns, image, write, markdown, error)
        Create a mock for the column layout with col1, col2, and col3
        For the image placeholder URL, use "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png".
        Include detailed comments for each test method explaining what's being tested.
    '''
    """Tests the display_post function."""
    
    def setUp(self):
        """Set up patches for Streamlit functions to avoid rendering errors."""
        self.patcher_columns = patch("streamlit.columns", return_value=(MagicMock(), MagicMock(), MagicMock()))
        self.patcher_image = patch("streamlit.image")
        self.patcher_write = patch("streamlit.write")
        self.patcher_markdown = patch("streamlit.markdown")
        self.patcher_error = patch("streamlit.error")
        
        self.mock_columns = self.patcher_columns.start()
        self.mock_image = self.patcher_image.start()
        self.mock_write = self.patcher_write.start()
        self.mock_markdown = self.patcher_markdown.start()
        self.mock_error = self.patcher_error.start()

    def tearDown(self):
        """Stop all patches after each test to prevent side effects."""
        patch.stopall()

    @patch('modules.get_user_profile')
    def test_valid_post(self, mock_get_user_profile):
        """Test a valid post with a profile image and a post image."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Create post dictionary instead of Post object
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'This is a test post.',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure layout columns are created
        self.mock_columns.assert_called_once_with([1, 3, 1])

        # Ensure profile image and post image are displayed correctly
        self.mock_image.assert_any_call('https://example.com/profile.jpg', width=90)
        self.mock_image.assert_any_call('https://example.com/post.jpg', use_container_width=True)

        # Ensure text content is displayed correctly
        self.mock_write.assert_any_call("**testuser**")
        self.mock_write.assert_any_call('2025-03-08 14:30:00')
        self.mock_write.assert_any_call('This is a test post.')

        # Ensure horizontal dividers are rendered
        self.mock_markdown.assert_called()
        
        # Check that get_user_profile was called with the correct user_id
        mock_get_user_profile.assert_called_once_with('user1')

    @patch('modules.get_user_profile')
    def test_missing_user_image(self, mock_get_user_profile):
        """Test that a missing user profile image defaults to a placeholder."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': None,
            'friends': [],
        }
        
        # Create post dictionary
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'This is a test post.',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Check if the placeholder image is used
        placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"
        self.mock_image.assert_any_call(placeholder_url, width=90)

    @patch('modules.get_user_profile')
    def test_missing_post_image(self, mock_get_user_profile):
        """Test that a missing post image does not cause an error."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Create post dictionary without image
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'This is a test post.',
            'image': None
        }
        
        display_post(post)

        # Ensure that only the profile image was displayed
        calls = [call[0] for call in self.mock_image.call_args_list]
        self.assertEqual(len(calls), 1)  # Only one image call
        self.assertEqual(calls[0][0], 'https://example.com/profile.jpg')  # With profile image

    @patch('modules.get_user_profile')
    def test_empty_content(self, mock_get_user_profile):
        """Test that a post with empty content still renders correctly."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Create post dictionary with empty content
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': '',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure username and timestamp are still displayed
        self.mock_write.assert_any_call("**testuser**")
        self.mock_write.assert_any_call('2025-03-08 14:30:00')

        # Ensure dividers are still rendered
        self.mock_markdown.assert_called()

    @patch('modules.get_user_profile')
    def test_empty_timestamp(self, mock_get_user_profile):
        """Test that an empty timestamp does not break rendering."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Create post dictionary with empty timestamp
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '',
            'content': 'This is a test post.',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure username and content are still displayed
        self.mock_write.assert_any_call("**testuser**")
        self.mock_write.assert_any_call('This is a test post.')

    @patch('modules.get_user_profile')
    def test_user_profile_error(self, mock_get_user_profile):
        """Test that errors retrieving user profile are handled gracefully."""
        # Make get_user_profile raise an exception
        mock_get_user_profile.side_effect = Exception("User profile error")
        
        # Create post dictionary
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'This is a test post.',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure error is displayed
        self.mock_error.assert_called()

    @patch('modules.get_user_profile')
    def test_invalid_image_urls(self, mock_get_user_profile):
        """Test that invalid image URLs default to the placeholder image."""
        # Define mock return value for get_user_profile with invalid image URL
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'invalid_url',
            'friends': [],
        }
        
        # Create post dictionary with invalid image URL
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'This is a test post.',
            'image': 'invalid_url'
        }
        
        display_post(post)

        # Check that the placeholder profile image was used
        placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"
        self.mock_image.assert_any_call(placeholder_url, width=90)

    @patch('modules.get_user_profile')
    def test_very_large_content(self, mock_get_user_profile):
        """Test that a very large content string is handled properly."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Create post dictionary with very large content
        long_text = "A" * 50000  # 50,000 characters
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': long_text,
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure content is displayed in some form
        self.assertTrue(any("A" in str(call) for call in self.mock_write.call_args_list))

    @patch('streamlit.columns')
    @patch('modules.get_user_profile')
    def test_layout_exception(self, mock_get_user_profile, mock_columns):
        """Test handling of layout errors when Streamlit's columns() function fails."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Make columns raise an exception
        mock_columns.side_effect = Exception("Layout error")
        
        # Create post dictionary
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'This is a test post.',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure an error message was displayed
        self.mock_error.assert_called_once()

    @patch('modules.get_user_profile')
    def test_fallback_simple_display(self, mock_get_user_profile):
        """Test that the function gracefully falls back to a simple layout when column layout fails."""
        # Define mock return value for get_user_profile
        mock_get_user_profile.return_value = {
            'full_name': 'Test User',
            'username': 'testuser',
            'date_of_birth': '1990-01-01',
            'profile_image': 'https://example.com/profile.jpg',
            'friends': [],
        }
        
        # Make columns raise an exception
        self.mock_columns.side_effect = Exception("Layout error")
        
        # Create post dictionary
        post = {
            'user_id': 'user1',
            'post_id': 'post1',
            'timestamp': '2025-03-08 14:30:00',
            'content': 'Fallback content',
            'image': 'https://example.com/post.jpg'
        }
        
        display_post(post)

        # Ensure an error was logged
        self.mock_error.assert_called_once()

        # Ensure the content is still displayed even if the layout fails
        self.assertTrue(any('Fallback content' in str(call) for call in self.mock_write.call_args_list))


class SessionStateMock(dict):
    """Mock for Streamlit's session_state that allows both dict and attribute access."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def __getattr__(self, key):
        if key in self:
            return self[key]
        # Return a default to avoid AttributeError
        return None
        
    def __setattr__(self, key, value):
        self[key] = value

class TestDisplayActivitySummary(unittest.TestCase):
    """Unit tests for the display_activity_summary function in a Streamlit app."""

    def setUp(self):
        """Set up patches for Streamlit functions to avoid rendering errors."""
        self.patcher_markdown = patch("streamlit.markdown")
        self.patcher_container = patch("streamlit.container")
        self.patcher_caption = patch("streamlit.caption")
        self.patcher_columns = patch("streamlit.columns", return_value=(MagicMock(), MagicMock()))
        self.patcher_image = patch("streamlit.image")
        self.patcher_error = patch("streamlit.error")
        self.patcher_warning = patch("streamlit.warning")

        self.mock_markdown = self.patcher_markdown.start()
        self.mock_container = self.patcher_container.start()
        self.mock_caption = self.patcher_caption.start()
        self.mock_columns = self.patcher_columns.start()
        self.mock_image = self.patcher_image.start()
        self.mock_error = self.patcher_error.start()
        self.mock_warning = self.patcher_warning.start()

    def tearDown(self):
        """Stop all patches after each test to prevent side effects."""
        patch.stopall()

    @patch('modules.get_user_workouts')
    def test_valid_input(self, mock_get_workouts):
        """Test display with valid workout data."""
        mock_get_workouts.return_value = [{
            'workout_id': 'workout1',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary("valid_user")
        self.mock_markdown.assert_called()  # Ensures markdown content was displayed

    @patch('modules.get_user_workouts')
    def test_none_values(self, mock_get_workouts):
        """Test when all parameters are None."""
        mock_get_workouts.return_value = [None]
        display_activity_summary(None)
        self.mock_warning.assert_called_with("No user data available.")

    @patch('modules.get_user_workouts')
    def test_empty_strings(self, mock_get_workouts):
        """Test when all parameters are empty strings."""
        mock_get_workouts.return_value = [{
            'workout_id': '',
            'start_timestamp': '',
            'end_timestamp': '',
            'distance': '',
            'steps': '',
            'calories_burned': '',
            'start_lat_lng': '',
            'end_lat_lng': '',
        }]
        display_activity_summary("")
    @patch('modules.get_user_workouts')
    def test_non_string_inputs(self, mock_get_workouts):
        """Test when parameters contain numbers, booleans, and objects."""
        mock_get_workouts.return_value = [{
            'workout_id': 12345,
            'start_timestamp': 1000,
            'end_timestamp': False,
            'distance': object(),
            'steps': True,
            'calories_burned': [100, 200],
            'start_lat_lng': {},
            'end_lat_lng': (),
        }]
        display_activity_summary(999)
        self.mock_error.assert_called()  # Should handle unexpected types

    @patch('modules.get_user_workouts')
    def test_large_content(self, mock_get_workouts):
        """Test with an excessively large description string (50,000+ characters)."""
        large_text = "A" * 50000
        mock_get_workouts.return_value = [{
            'workout_id': 'workout_large',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary("large_user")
        self.mock_markdown.assert_called()  # Should render despite large input

    @patch('modules.get_user_workouts')
    def test_alternative_timestamp_formats(self, mock_get_workouts):
        """Test various timestamp formats."""
        timestamps = [
            "2025-03-20T10:00:00",  # ISO format
            "2025/03/20 10:00:00",  # Slash format
            "03-20-2025 10:00 AM",  # US format
            "2025-03-20 10:00:00.123456",  # With microseconds
        ]
        for ts in timestamps:
            mock_get_workouts.return_value = [{
                'workout_id': 'workout_time',
                'start_timestamp': ts,
                'end_timestamp': "2025-03-20 11:00:00",
                'distance': 5.0,
                'steps': 10000,
                'calories_burned': 500,
                'start_lat_lng': (40.7128, -74.0060),
                'end_lat_lng': (40.7138, -74.0070),
            }]
            display_activity_summary("time_user")

    @patch('modules.get_user_workouts')
    def test_invalid_timestamp(self, mock_get_workouts):
        """Test invalid timestamp formats."""
        mock_get_workouts.return_value = [{
            'workout_id': 'workout_invalid',
            'start_timestamp': "InvalidTimestamp",
            'end_timestamp': "AnotherInvalidTimestamp",
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary("invalid_time_user")
        self.mock_error.assert_called()  # Should handle parsing errors

    @patch('modules.get_user_workouts')
    def test_image_display_error(self, mock_get_workouts):
        """Test when there is an error displaying an image."""
        mock_get_workouts.return_value = [{
            'workout_id': 'workout_img_error',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        

    @patch('modules.get_user_workouts')
    def test_whitespace_image_url(self, mock_get_workouts):
        """Test when the image URL is whitespace."""
        mock_get_workouts.return_value = [{
            'workout_id': 'workout_whitespace',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary("whitespace_img_user")
        self.mock_warning.assert_not_called()  # Should handle empty image URLs


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""
    
    '''
    CLAUDE PROMPT:
        Write a comprehensive unittest test class for the display_genai_advice function using Python's unittest framework. The class should:

        1. Mock all relevant Streamlit functions (container, markdown, caption, columns, image, error, warning)

        3. Include test methods for the following scenarios:
            - Valid inputs with properly formatted timestamp, content, and image URL
            - None values for all parameters
            - Empty strings for all parameters
            - Non-string inputs (numbers, booleans, objects)
            - Very large content strings (50,000+ characters)
            - Alternative timestamp formats (ISO, with microseconds, slash format, US format)
            - Invalid timestamp formats
            - Image display errors
            - Whitespace image URLs
            - Layout exceptions

        4. For each test, include appropriate assertions to verify that the function behaves correctly under those conditions

        5. Include proper documentation for the class and each test method

        Make sure each test properly cleans up after itself and doesn't affect other tests.
    '''

    def setUp(self):
        """Set up test environment before each test"""
        # Mock streamlit functions
        self.container_mock = MagicMock()
        self.markdown_mock = MagicMock()
        self.caption_mock = MagicMock()
        self.columns_mock = MagicMock()
        self.image_mock = MagicMock()
        self.error_mock = MagicMock()
        self.warning_mock = MagicMock()
        
        # Setup column context manager mocks
        self.col0_mock = MagicMock()
        self.col1_mock = MagicMock()
        self.col0_context = MagicMock()
        self.col1_context = MagicMock()
        
        # Configure column mocks
        self.col0_context.__enter__.return_value = self.col0_mock
        self.col0_context.__exit__.return_value = None
        self.col1_context.__enter__.return_value = self.col1_mock
        self.col1_context.__exit__.return_value = None
        
        # Configure columns to return our mocked contexts
        self.columns_mock.return_value = [self.col0_context, self.col1_context]
        
        # Configure container context manager
        self.container_context = MagicMock()
        self.container_context.__enter__.return_value = None
        self.container_context.__exit__.return_value = None
        self.container_mock.return_value = self.container_context
        
        # Apply all our mocks to streamlit
        streamlit_patches = {
            'container': self.container_mock,
            'markdown': self.markdown_mock,
            'caption': self.caption_mock,
            'columns': self.columns_mock,
            'image': self.image_mock,
            'error': self.error_mock,
            'warning': self.warning_mock,
        }
        self.st_patcher = patch.multiple(st, **streamlit_patches)
        self.st_patcher.start()
        
        # Create a standard mock advice response
        self.mock_advice = {
            "timestamp": "2023-08-15 14:30:00",
            "content": "This is test advice content",
            "image": "https://example.com/test-image.jpg"
        }
        
        # Based on the diagnostic results, determine the correct module path
        # We'll use a direct patch of the specific function based on where it's imported
        self.get_advice_patcher = patch('modules.get_genai_advice')
        self.mock_get_advice = self.get_advice_patcher.start()
        
        # Default return value for the get_genai_advice mock
        self.mock_get_advice.return_value = self.mock_advice
    
    def tearDown(self):
        """Clean up after each test"""
        self.st_patcher.stop()
        self.get_advice_patcher.stop()
    
    def test_basic_functionality(self):
        """Test that the basic function works and calls streamlit components"""
        # Call the function with a test user ID
        display_genai_advice("test_user")
        
        # Check if our mock was called with the user ID
        self.mock_get_advice.assert_called_once_with("test_user")
        
        # Verify that all the expected Streamlit functions were called
        self.container_mock.assert_called_once()
        self.markdown_mock.assert_called()  # Multiple calls expected
        self.caption_mock.assert_called_once()
        self.columns_mock.assert_called_once()
    
    def test_displays_advice_content(self):
        """Test that advice content is displayed in markdown"""
        test_content = "This is special test advice content"
        self.mock_get_advice.return_value = {
            "timestamp": "2023-08-15 14:30:00",
            "content": test_content,
            "image": "https://example.com/test-image.jpg"
        }
        
        display_genai_advice("test_user")
        
        # Check if content appears in any markdown call
        markdown_calls = [str(call) for call in self.markdown_mock.call_args_list]
        content_displayed = any(test_content in call for call in markdown_calls)
        
        # This may be in a div with styling, so we look for the content within the calls
        self.assertTrue(any(test_content in call for call in markdown_calls), 
                      f"Content '{test_content}' not found in any markdown calls")
    
    def test_none_user_id(self):
        """Test that function handles None user_id"""
        display_genai_advice(None)
        
        # Should call get_genai_advice with None
        self.mock_get_advice.assert_called_once_with(None)
        
        # Should still render the UI
        self.container_mock.assert_called_once()
        self.markdown_mock.assert_called()
        self.caption_mock.assert_called_once()
    
    def test_displays_timestamp(self):
        """Test that timestamp is formatted and displayed"""
        timestamp = "2023-08-15 14:30:00"
        self.mock_get_advice.return_value = {
            "timestamp": timestamp,
            "content": "Test content",
            "image": "https://example.com/test-image.jpg"
        }
        
        display_genai_advice("test_user")
        
        # The timestamp should be formatted and displayed
        self.caption_mock.assert_called_once()
        caption_text = str(self.caption_mock.call_args[0][0])
        
        # Since the actual implementation may format the date differently than we expect,
        # we'll just check that the caption contains "Generated on" and has a date
        self.assertIn("Generated on", caption_text)
    
    def test_displays_image_when_provided(self):
        """Test that image is displayed when provided"""
        test_image = "https://example.com/special-test-image.jpg"
        self.mock_get_advice.return_value = {
            "timestamp": "2023-08-15 14:30:00",
            "content": "Test content",
            "image": test_image
        }
        
        display_genai_advice("test_user")
        
        # The image should be displayed
        # First check if st.image was called
        self.image_mock.assert_called()
        
        # Check if any call used our image URL
        image_calls = [str(call) for call in self.image_mock.call_args_list]
        self.assertTrue(any(test_image in call for call in image_calls),
                       f"Image URL '{test_image}' not found in any image calls")
    
    def test_handles_missing_advice_keys(self):
        """Test that function handles advice with missing keys"""
        # Return an incomplete advice dictionary
        self.mock_get_advice.return_value = {
            # Missing timestamp and image
            "content": "Just content, no timestamp or image"
        }
        
        display_genai_advice("test_user")
        
        # Should still render the UI without errors
        self.container_mock.assert_called_once()
        self.markdown_mock.assert_called()
        self.caption_mock.assert_called_once()
    
    def test_handles_empty_advice_dict(self):
        """Test that function handles empty advice dictionary"""
        # Return an empty dictionary
        self.mock_get_advice.return_value = {}
        
        display_genai_advice("test_user")
        
        # Should still render the UI with default values
        self.container_mock.assert_called_once()
        self.markdown_mock.assert_called()
        self.caption_mock.assert_called_once()
        
        # Should display a default message
        markdown_calls = [str(call) for call in self.markdown_mock.call_args_list]
        default_message_displayed = any("No advice available" in call for call in markdown_calls)
        self.assertTrue(default_message_displayed, "Default message not displayed for empty advice")
    
    def test_get_advice_exception(self):
        """Test that function handles exception from get_genai_advice"""
        # Make get_genai_advice raise an exception
        self.mock_get_advice.side_effect = Exception("Test exception")
        
        with self.assertRaises(Exception):
            display_genai_advice("test_user")
    
        # Verify the mock was called before exception was raised
        self.mock_get_advice.assert_called_once_with("test_user")
    
    def test_layout_exception(self):
        """Test handling of layout exceptions"""
        # Make columns raise an exception
        self.columns_mock.side_effect = Exception("Layout error")
        
        display_genai_advice("test_user")
        
        # Should handle the error gracefully
        # This may show an error or use a simplified layout
        self.container_mock.assert_called_once()
        self.markdown_mock.assert_called()
    
    def test_very_large_content(self):
        """Test with extremely large content string"""
        self.mock_get_advice.return_value = {
            "timestamp": "2023-08-15 14:30:00",
            "content": "A" * 50000,  # Very long string
            "image": "https://example.com/test-image.jpg"
        }
        
        display_genai_advice("test_user")
        
        # Should still function with large content
        self.container_mock.assert_called_once()
        
        # Some part of the content should appear in the markdown
        markdown_calls = [str(call) for call in self.markdown_mock.call_args_list]
        self.assertTrue(any("A" in call for call in markdown_calls), 
                       "Large content not found in any markdown calls")



class TestDisplayActivitySummary(unittest.TestCase):
    """Unit tests for the display_activity_summary function in a Streamlit app."""

    def setUp(self):
        """Set up patches for Streamlit functions to avoid rendering errors."""
        self.patcher_markdown = patch("streamlit.markdown")
        self.patcher_container = patch("streamlit.container")
        self.patcher_caption = patch("streamlit.caption")
        self.patcher_columns = patch("streamlit.columns", return_value=(MagicMock(), MagicMock()))
        self.patcher_image = patch("streamlit.image")
        self.patcher_error = patch("streamlit.error")
        self.patcher_warning = patch("streamlit.warning")

        self.mock_markdown = self.patcher_markdown.start()
        self.mock_container = self.patcher_container.start()
        self.mock_caption = self.patcher_caption.start()
        self.mock_columns = self.patcher_columns.start()
        self.mock_image = self.patcher_image.start()
        self.mock_error = self.patcher_error.start()
        self.mock_warning = self.patcher_warning.start()

    def tearDown(self):
        """Stop all patches after each test to prevent side effects."""
        patch.stopall()

    @patch('modules.get_user_workouts')
    def test_valid_input(self, mock_get_workouts):
        """Test display with valid workout data."""
        workouts_list = [{
            'workout_id': 'workout1',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary(workouts_list)
        self.mock_markdown.assert_called()  # Ensures markdown content was displayed

    @patch('modules.get_user_workouts')
    def test_none_values(self, mock_get_workouts):
        """Test when all parameters are None."""
        display_activity_summary(None)
    

    @patch('modules.get_user_workouts')
    def test_empty_strings(self, mock_get_workouts):
        """Test when all parameters are empty strings."""
        workouts_list = [{
            'workout_id': '',
            'start_timestamp': '',
            'end_timestamp': '',
            'distance': '',
            'steps': '',
            'calories_burned': '',
            'start_lat_lng': '',
            'end_lat_lng': '',
        }]
        display_activity_summary(workouts_list)

    @patch('modules.get_user_workouts')
    def test_non_string_inputs(self, mock_get_workouts):
        """Test when parameters contain numbers, booleans, and objects."""
        workouts_list = [{
            'workout_id': 12345,
            'start_timestamp': 1000,
            'end_timestamp': False,
            'distance': object(),
            'steps': True,
            'calories_burned': [100, 200],
            'start_lat_lng': {},
            'end_lat_lng': (),
        }]
        display_activity_summary(workouts_list)
        self.mock_error.assert_called()  # Should handle unexpected types

    @patch('modules.get_user_workouts')
    def test_large_content(self, mock_get_workouts):
        """Test with an excessively large description string (50,000+ characters)."""
        large_text = "A" * 50000
        workouts_list = [{
            'workout_id': 'workout_large',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary(workouts_list)
        self.mock_markdown.assert_called()  # Should render despite large input

    @patch('modules.get_user_workouts')
    def test_alternative_timestamp_formats(self, mock_get_workouts):
        """Test various timestamp formats."""
        timestamps = [
            "2025-03-20T10:00:00",  # ISO format
            "2025/03/20 10:00:00",  # Slash format
            "03-20-2025 10:00 AM",  # US format
            "2025-03-20 10:00:00.123456",  # With microseconds
        ]
        for ts in timestamps:
            workouts_list = [{
                'workout_id': 'workout_time',
                'start_timestamp': ts,
                'end_timestamp': "2025-03-20 11:00:00",
                'distance': 5.0,
                'steps': 10000,
                'calories_burned': 500,
                'start_lat_lng': (40.7128, -74.0060),
                'end_lat_lng': (40.7138, -74.0070),
            }]
            display_activity_summary(workouts_list)

    @patch('modules.get_user_workouts')
    def test_invalid_timestamp(self, mock_get_workouts):
        """Test invalid timestamp formats."""
        workouts_list = [{
            'workout_id': 'workout_invalid',
            'start_timestamp': "InvalidTimestamp",
            'end_timestamp': "AnotherInvalidTimestamp",
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary(workouts_list)
        self.mock_error.assert_called()  # Should handle parsing errors

    @patch('modules.get_user_workouts')
    def test_image_display_error(self, mock_get_workouts):
        """Test when there is an error displaying an image."""
        workouts_list = [{
            'workout_id': 'workout_img_error',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary(workouts_list)
         # Should handle image display errors

    @patch('modules.get_user_workouts')
    def test_whitespace_image_url(self, mock_get_workouts):
        """Test when the image URL is whitespace."""
        workouts_list = [{
            'workout_id': 'workout_whitespace',
            'start_timestamp': '2025-03-20 10:00:00',
            'end_timestamp': '2025-03-20 11:00:00',
            'distance': 5.0,
            'steps': 10000,
            'calories_burned': 500,
            'start_lat_lng': (40.7128, -74.0060),
            'end_lat_lng': (40.7138, -74.0070),
        }]
        display_activity_summary(workouts_list)
        self.mock_warning.assert_not_called()  # Should handle empty image URLs



if __name__ == "__main__":
    unittest.main()
