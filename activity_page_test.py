import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from activity_page import display_activity_page, display_activity_summary, create_post

# python3 -m unittest activity_page_test.py
'''
AI Prompt:

Create a comprehensive unit test file named activity_page_test.py 
for the activity_page.py module using Python's unittest framework.
The tests should cover all major functions (display_activity_page, 
display_activity_summary, create_post) 

Use unittest.TestCase for all test classes.

Mock external dependencies (e.g., BigQuery, Streamlit, Folium) using unittest.mock.patch.

Include setup/teardown logic where necessary.
'''

class TestActivityPage(unittest.TestCase):
    
    @patch('activity_page.get_user_workouts')
    @patch('activity_page.get_user_profile')
    @patch('activity_page.st.title')
    @patch('activity_page.st.tabs')
    def test_no_workouts(self, mock_tabs, mock_title, mock_get_profile, mock_get_workouts):
        """Test behavior when no workouts are found."""
        # Setup mocks
        mock_get_workouts.return_value = []
        mock_get_profile.return_value = {'username': 'testuser'}
        mock_info = MagicMock()
        
        with patch('activity_page.st.info', mock_info):
            # Call function with test user ID
            display_activity_page('user1')
            
            # Verify title was set and info message was shown
            mock_title.assert_called_once_with("Your Activity")
            mock_info.assert_called_once_with("No workouts found.")
            
            # Verify tabs were not created
            mock_tabs.assert_not_called()
    
    @patch('activity_page.get_user_workouts')
    @patch('activity_page.get_user_profile')
    @patch('activity_page.st.title')
    @patch('activity_page.st.tabs')
    @patch('activity_page.display_activity_summary')
    def test_with_workouts(self, mock_display_summary, mock_tabs, mock_title, 
                          mock_get_profile, mock_get_workouts):
        """Test that the page displays correctly with workouts."""
        # Setup mock data
        mock_workouts = [
            {
                'workout_id': 'workout1',
                'start_timestamp': '2025-04-06 08:00:00',
                'end_timestamp': '2025-04-06 09:00:00',
                'distance': 5.0,
                'steps': 8000,
                'calories_burned': 400
            },
            {
                'workout_id': 'workout2',
                'start_timestamp': '2025-04-05 08:00:00',
                'end_timestamp': '2025-04-05 09:30:00',
                'distance': 6.2,
                'steps': 10000,
                'calories_burned': 500
            }
        ]
        mock_get_workouts.return_value = mock_workouts
        mock_get_profile.return_value = {'username': 'testuser'}
        
        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tabs.return_value = [mock_tab1, mock_tab2]
        
        # Mock subheader, markdown, and button functions
        with patch('activity_page.st.subheader') as mock_subheader:
            with patch('activity_page.st.markdown') as mock_markdown:
                with patch('activity_page.st.button', return_value=False) as mock_button:
                    # Call the function
                    display_activity_page('user1')
                    
                    # Verify title was set
                    mock_title.assert_called_once_with("Your Activity")
                    
                    # Verify tabs were created
                    mock_tabs.assert_called_once()
                    
                    # Verify subheaders were created in the first tab
                    mock_tab1.__enter__.assert_called()
                    mock_subheader.assert_any_call("All Workouts")
                    mock_subheader.assert_any_call("Activity Summary")
                    
                    # Verify markdown calls include workout details
                    self.assertGreaterEqual(mock_markdown.call_count, 15)  # Multiple calls expected
                    
                    # Verify activity summary was called in the second tab
                    mock_tab2.__enter__.assert_called()
                    mock_display_summary.assert_called_once_with('user1')
    
    @patch('activity_page.get_user_workouts')
    @patch('activity_page.get_user_profile')
    @patch('activity_page.st.title')
    @patch('activity_page.st.tabs')
    @patch('activity_page.display_activity_summary')
    @patch('activity_page.create_post')
    def test_sharing_workout(self, mock_create_post, mock_display_summary, mock_tabs, 
                            mock_title, mock_get_profile, mock_get_workouts):
        """Test the share workout functionality."""
        # Setup mock data
        mock_workouts = [
            {
                'workout_id': 'workout1',
                'start_timestamp': '2025-04-06 08:00:00',
                'end_timestamp': '2025-04-06 09:00:00',
                'distance': 5.0,
                'steps': 8000,
                'calories_burned': 400
            }
        ]
        mock_get_workouts.return_value = mock_workouts
        mock_get_profile.return_value = {'username': 'testuser'}
        
        # Mock tabs
        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tabs.return_value = [mock_tab1, mock_tab2]
        
        # Mock button to return True (simulate button click)
        with patch('activity_page.st.subheader'):
            with patch('activity_page.st.markdown'):
                with patch('activity_page.st.button', return_value=True) as mock_button:
                    # Call the function
                    display_activity_page('user1')
                    
                    # Verify create_post was called
                    expected_content = "Look at this, I walked 8000 steps today!"
                    mock_create_post.assert_called_with('user1', expected_content)

class TestDisplayActivitySummary(unittest.TestCase):
    
    @patch('activity_page.get_user_workouts')
    @patch('activity_page.st.warning')
    def test_no_user_id(self, mock_warning, mock_get_workouts):
        """Test behavior when no user ID is provided."""
        # Call function with empty user ID
        display_activity_summary('')
        
        # Verify warning was shown
        mock_warning.assert_called_once_with("No user data available.")
        
        # Verify get_user_workouts was not called
        mock_get_workouts.assert_not_called()
    
    @patch('activity_page.get_user_workouts')
    @patch('activity_page.st.info')
    def test_no_workouts(self, mock_info, mock_get_workouts):
        """Test behavior when no workouts are found."""
        # Setup mock
        mock_get_workouts.return_value = []
        
        # Call function
        display_activity_summary('user1')
        
        # Verify info message was shown
        mock_info.assert_called_once_with("No workout data available.")
    
    @patch('activity_page.get_user_workouts')
    @patch('activity_page.folium.Map')
    @patch('activity_page.folium.Marker')
    @patch('activity_page.st_folium')
    def test_with_workouts(self, mock_st_folium, mock_marker, mock_map, mock_get_workouts):
        """Test summary display with workout data."""
        # Setup mock data with complete workout info
        mock_workouts = [
            {
                'workout_id': 'workout1',
                'start_timestamp': '2025-04-06 08:00:00',
                'end_timestamp': '2025-04-06 09:00:00',
                'distance': 5.0,
                'steps': 8000,
                'calories_burned': 400,
                'start_lat_lng': (37.7749, -122.4194),
                'end_lat_lng': (37.7750, -122.4195)
            }
        ]
        mock_get_workouts.return_value = mock_workouts
        
        # Mock Map and Marker
        mock_map_instance = MagicMock()
        mock_map.return_value = mock_map_instance
        mock_marker_instance = MagicMock()
        mock_marker.return_value = mock_marker_instance
        
        # Mock session state
        if not hasattr(st, 'session_state'):
            setattr(st, 'session_state', {})
        st.session_state.map_rendered = False
        
        # Mock columns and markdown
        with patch('activity_page.st.columns') as mock_columns:
            with patch('activity_page.st.markdown') as mock_markdown:
                # Setup mock columns
                mock_col1 = MagicMock()
                mock_col2 = MagicMock()
                mock_columns.return_value = [mock_col1, mock_col2]
                
                # Call function
                display_activity_summary('user1')
                
                # Verify maps were created
                self.assertEqual(mock_map.call_count, 2)  # Start and end maps
                self.assertEqual(mock_marker.call_count, 2)  # Start and end markers
                self.assertEqual(mock_st_folium.call_count, 2)  # Maps displayed
                
                # Verify session state was updated
                self.assertTrue(st.session_state.map_rendered)

class TestCreatePost(unittest.TestCase):
    
    @patch('activity_page.bigquery.Client')
    @patch('activity_page.uuid.uuid4')
    @patch('activity_page.datetime')
    @patch('activity_page.st.success')
    def test_successful_post_creation(self, mock_success, mock_datetime, mock_uuid, mock_client):
        """Test successful post creation."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.insert_rows_json.return_value = []  # Empty list means no errors
        
        # Mock UUID
        mock_uuid.return_value = "test-uuid-123"
        
        # Mock datetime
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025-04-06 10:00:00.000000"
        mock_datetime.now.return_value = mock_now
        
        # Call function
        create_post('user1', 'Test post content', 'http://example.com/image.jpg')
        
        # Verify client was called with correct data
        expected_row = [{
            "PostId": "test-uuid-123",
            "AuthorId": 'user1',
            "Timestamp": "2025-04-06 10:00:00.000000",
            "ImageUrl": 'http://example.com/image.jpg',
            "Content": 'Test post content'
        }]
        mock_client_instance.insert_rows_json.assert_called_once_with(
            "bamboo-creek-450920-h2.ISE.Posts", expected_row)
        
        # Verify success message
        mock_success.assert_called_once_with("Post inserted successfully!")
    
    @patch('activity_page.bigquery.Client')
    @patch('activity_page.uuid.uuid4')
    @patch('activity_page.datetime')
    @patch('activity_page.st.error')
    def test_post_creation_error(self, mock_error, mock_datetime, mock_uuid, mock_client):
        """Test behavior when post creation fails."""
        # Setup mocks
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        # Return errors from insert_rows_json
        mock_client_instance.insert_rows_json.return_value = ["Error: Something went wrong"]
        
        # Mock UUID
        mock_uuid.return_value = "test-uuid-123"
        
        # Mock datetime
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2025-04-06 10:00:00.000000"
        mock_datetime.now.return_value = mock_now
        
        # Call function
        create_post('user1', 'Test post content')
        
        # Verify error message
        mock_error.assert_called_once()

if __name__ == '__main__':
    unittest.main()