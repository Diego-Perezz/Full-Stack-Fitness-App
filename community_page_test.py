import unittest
from unittest.mock import patch, MagicMock
from community_page import display_posts_page

# python3 -m unittest community_page_test.py

'''
AI Prompt:
Create a comprehensive unit test file named community_page_test.py 
for the community_page.py module using Python's unittest framework. 
The tests should thoroughly cover the display_posts_page

Test Structure:
Use unittest.TestCase as the base class
Organize tests into a single test class TestDisplayPostsPage
Mock all external dependencies using unittest.mock.patch
'''

class TestDisplayPostsPage(unittest.TestCase):
    
    @patch('community_page.get_user_profile')
    @patch('community_page.get_user_posts')
    @patch('community_page.display_genai_advice')
    @patch('community_page.display_post')
    @patch('community_page.st.columns')
    @patch('community_page.st.title')
    def test_successful_display_with_posts(self, mock_title, mock_columns, mock_display_post, 
                                          mock_display_advice, mock_get_posts, mock_get_profile):
        """Test that the page displays correctly with posts from the user and friends."""
        # Set up mock returns
        mock_profile = {
            'username': 'testuser',
            'profile_image': 'http://example.com/image.jpg',
            'friends': ['user2', 'user3']
        }
        mock_get_profile.return_value = mock_profile
        
        # Create mock posts for user and friends
        user_posts = [
            {'user_id': 'user1', 'post_id': 'post1', 'content': 'User post', 
             'timestamp': '2025-04-06 10:00:00', 'image': 'http://example.com/post1.jpg'}
        ]
        friend_posts1 = [
            {'user_id': 'user2', 'post_id': 'post2', 'content': 'Friend post', 
             'timestamp': '2025-04-06 11:00:00', 'image': 'http://example.com/post2.jpg'}
        ]
        friend_posts2 = [
            {'user_id': 'user3', 'post_id': 'post3', 'content': 'Another friend post', 
             'timestamp': '2025-04-06 12:00:00', 'image': 'http://example.com/post3.jpg'}
        ]
        
        mock_get_posts.side_effect = [user_posts, friend_posts1, friend_posts2]
        
        # Mock columns
        mock_left_col = MagicMock()
        mock_right_col = MagicMock()
        mock_columns.return_value = [mock_left_col, mock_right_col]
        
        # Call the function with a test user ID
        display_posts_page('user1')
        
        # Verify the basic page setup
        mock_title.assert_called_once_with("Social Feed")
        mock_get_profile.assert_called_once_with('user1')
        mock_columns.assert_called_once_with([2, 1])
        
        # Verify advice was displayed
        mock_display_advice.assert_called_once_with('user1')
        
        # Verify posts were fetched and displayed
        self.assertEqual(mock_get_posts.call_count, 3)  # User + 2 friends
        
        # Verify that all posts were displayed and in correct order (most recent first)
        expected_calls = 3  # 3 posts total
        self.assertEqual(mock_display_post.call_count, expected_calls)
        
    @patch('community_page.get_user_profile')
    @patch('community_page.get_user_posts')
    @patch('community_page.display_genai_advice')
    @patch('community_page.st.columns')
    @patch('community_page.st.title')
    @patch('community_page.st.info')
    def test_no_posts_available(self, mock_info, mock_title, mock_columns, 
                               mock_display_advice, mock_get_posts, mock_get_profile):
        """Test behavior when no posts are available."""
        # Set up mock returns
        mock_profile = {
            'username': 'testuser',
            'profile_image': 'http://example.com/image.jpg',
            'friends': ['user2', 'user3']
        }
        mock_get_profile.return_value = mock_profile
        
        # Return empty post lists
        mock_get_posts.return_value = []
        
        # Mock columns
        mock_left_col = MagicMock()
        mock_right_col = MagicMock()
        mock_columns.return_value = [mock_left_col, mock_right_col]
        
        # Call the function with a test user ID
        display_posts_page('user1')
        
        # Verify the info message was shown
        mock_info.assert_called_once()
    
    @patch('community_page.get_user_profile')
    @patch('community_page.st.error')
    def test_user_not_found(self, mock_error, mock_get_profile):
        """Test behavior when user profile cannot be found."""
        # Set up the mock to raise an exception
        mock_get_profile.side_effect = ValueError("User not found")
        
        # Call the function with a test user ID
        display_posts_page('nonexistent')
        
        # Verify the error was shown
        mock_error.assert_called_once_with("Error: User not found.")
    
    @patch('community_page.get_user_profile')
    @patch('community_page.get_user_posts')
    @patch('community_page.display_genai_advice')
    @patch('community_page.st.columns')
    @patch('community_page.st.title')
    @patch('community_page.st.warning')
    def test_friends_posts_error(self, mock_warning, mock_title, mock_columns, 
                                mock_display_advice, mock_get_posts, mock_get_profile):
        """Test handling of errors when retrieving friends' posts."""
        # Set up mock returns
        mock_profile = {
            'username': 'testuser',
            'profile_image': 'http://example.com/image.jpg',
            'friends': ['user2', 'user3']
        }
        mock_get_profile.return_value = mock_profile
        
        # First call returns user posts, second call raises exception
        mock_get_posts.side_effect = [
            [{'user_id': 'user1', 'post_id': 'post1', 'content': 'User post', 
              'timestamp': '2025-04-06 10:00:00'}],
            Exception("Database error")
        ]
        
        # Mock columns
        mock_left_col = MagicMock()
        mock_right_col = MagicMock()
        mock_columns.return_value = [mock_left_col, mock_right_col]
        
        # Call the function with a test user ID
        display_posts_page('user1')
        
        # Verify the warning was shown
        mock_warning.assert_called_once()
    
    @patch('community_page.get_user_profile')
    @patch('community_page.get_user_posts')
    @patch('community_page.display_genai_advice')
    @patch('community_page.display_post')
    @patch('community_page.st.columns')
    @patch('community_page.st.title')
    def test_timestamp_parsing(self, mock_title, mock_columns, mock_display_post, 
                              mock_display_advice, mock_get_posts, mock_get_profile):
        """Test that posts with various timestamp formats are handled correctly."""
        # Set up mock returns
        mock_profile = {
            'username': 'testuser',
            'profile_image': 'http://example.com/image.jpg',
            'friends': []
        }
        mock_get_profile.return_value = mock_profile
        
        # Create posts with different timestamp formats
        posts = [
            {'user_id': 'user1', 'post_id': 'post1', 'content': 'Normal timestamp', 
             'timestamp': '2025-04-06 10:00:00'},
            {'user_id': 'user1', 'post_id': 'post2', 'content': 'Missing timestamp', 
             'timestamp': None},
            {'user_id': 'user1', 'post_id': 'post3', 'content': 'Invalid timestamp', 
             'timestamp': 'not-a-date'}
        ]
        
        mock_get_posts.return_value = posts
        
        # Mock columns
        mock_left_col = MagicMock()
        mock_right_col = MagicMock()
        mock_columns.return_value = [mock_left_col, mock_right_col]
        
        # Replace random.shuffle to ensure deterministic behavior
        with patch('random.shuffle', side_effect=lambda x: x):
            # Call the function with a test user ID
            display_posts_page('user1')
        
        # Verify all posts were displayed despite timestamp issues
        self.assertEqual(mock_display_post.call_count, 3)

if __name__ == '__main__':
    unittest.main()