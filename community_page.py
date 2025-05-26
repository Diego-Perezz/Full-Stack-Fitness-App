from data_fetcher import get_user_profile, get_user_posts
from modules import display_genai_advice
import streamlit as st
from modules import display_post
from datetime import datetime

'''
AI Prompt:

Create a Streamlit module named community_page.py that implements 
a social media feed for a fitness community

Main Functionality:
Display a social feed showing posts from the user and their friends
Include functionality to create new posts
Show personalized AI generated fitness advice using the display_genai_advice function
'''


def display_posts_page(user_id):
    '''
    Displays a social media feed showing posts from a user and their friends.
    Includes functionality to create new posts.
    '''
    st.title("Social Feed")
    
    # Fetch user profile safely
    try:
        user_profile = get_user_profile(user_id)
        username = user_profile.get("username", "Unknown")
        user_image = user_profile.get("profile_image", None)
    except ValueError:
        st.error("Error: User not found.")
        return

    # Create two columns for the layout
    left_col, right_col = st.columns([2, 1])
    
    with right_col:
        # Display personalized AI advice in the right sidebar
        st.markdown("### Your Fitness Insights")
        display_genai_advice(user_id)
        
        # Create new post section in the right sidebar for better space usage
        with st.expander("Create a new post", expanded=False):
            post_content = st.text_area("What's on your mind?", height=100)
            post_image_url = st.text_input("Add image URL (optional)")
            
            if st.button("Post"):
                if post_content:
                    st.success("Post created successfully! (Note: This is a demo, post won't actually be saved)")
                    st.balloons()
                else:
                    st.warning("Please enter some content for your post")
    
    with left_col:
        # Fetch user posts
        user_posts = get_user_posts(user_id)
        
        # Also show friends' posts
        all_posts = user_posts.copy()  # Start with user's own posts
        try:
            friends = user_profile.get('friends', [])
            for friend_id in friends:
                friend_posts = get_user_posts(friend_id)
                if friend_posts:
                    all_posts.extend(friend_posts)
        except Exception as e:
            st.warning(f"Could not retrieve friends' posts: {str(e)}")
        
        # Display posts if any exist
        if all_posts:
            # Convert string timestamps to datetime objects for proper sorting
            for post in all_posts:
                # Handle any missing timestamps by setting a default old date
                if post.get('timestamp'):
                    try:
                        post['datetime'] = datetime.strptime(post['timestamp'], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        post['datetime'] = datetime(1970, 1, 1)  # Default old date if parsing fails
                else:
                    post['datetime'] = datetime(1970, 1, 1)  # Default old date if timestamp is missing
            
            # Sort posts by datetime, most recent first
            all_posts.sort(key=lambda x: x['datetime'], reverse=True)
            
            st.subheader("Recent Posts")
            
            # Display each post individually using the display_post function
            for post in all_posts:
                display_post(post)
        else:
            st.info("No posts available. Create your first post!")