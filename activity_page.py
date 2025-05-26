"""
activity_page.py

This module displays a user's activity page. It includes:
  - All workouts (using get_user_workouts)
  - An activity summary (aggregating statistics from the workouts)
  - A detailed activity summary with maps
  - A "Share" button that lets the user share a statistic (e.g., step count)
    with the community by inserting a row into the Posts table.
"""

'''
AI Prompt:

Create a Streamlit module named activity_page.py that displays a user's fitness activity page with the following features:

Functionality:

Fetch and display all workouts for a user using get_user_workouts 
Show an activity summary aggregating statistics across all workouts.
Include a detailed workout view with maps for start/end locations of each workout.
Implement a "Share" button to post workout statistics to a community feed by inserting a row into a BigQuery Posts table.
'''

import streamlit as st
from data_fetcher import get_user_workouts, get_user_profile
from google.cloud import bigquery
from datetime import datetime, timezone
import uuid
import folium
from streamlit_folium import st_folium

def create_post(user_id, content, image_url=None):
    """
    Inserts a new post into the Posts table in BigQuery.
    
    Parameters:
      user_id (str): The ID of the user creating the post.
      content (str): The text content of the post.
      image_url (str, optional): URL for an image associated with the post.
    
    Returns:
      None. Displays a success or error message.
    """
    client = bigquery.Client(project="bamboo-creek-450920-h2")
    table_id = "bamboo-creek-450920-h2.ISE.Posts"
    post_id = str(uuid.uuid4())
    # Format the timestamp in a BigQuery-friendly format.
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    
    row_to_insert = [{
        "PostId": post_id,
        "AuthorId": user_id,
        "Timestamp": now,
        "ImageUrl": image_url,
        "Content": content
    }]
    
    errors = client.insert_rows_json(table_id, row_to_insert)
    if not errors:
        st.success("Post inserted successfully!")
    else:
        st.error(f"Errors occurred while inserting the post: {errors}")

def display_activity_summary(user_id):
    '''
    Displays a detailed activity summary with workout metrics, timestamps, 
    and maps for each workout.
    
    Parameters:
        user_id (str): The ID of the user to display activities for.
    '''
    if not user_id:
        st.warning("No user data available.")
        return

    # Fetch workout data
    workouts_list = get_user_workouts(user_id)
    
    if not workouts_list:
        st.info("No workout data available.")
        return

    # Initialize session state if not exists
    if 'map_rendered' not in st.session_state:
        st.session_state.map_rendered = False

    # Process each workout in the list
    for i, workout in enumerate(workouts_list):
        try:
            # Extract workout ID and number
            workout_id = workout.get('workout_id', f'workout{i+1}')
            workout_num = workout_id.replace('workout', '') if 'workout' in workout_id else i+1

            # Process timestamps and calculate duration
            start_time_str = workout.get('start_timestamp')
            end_time_str = workout.get('end_timestamp')

            if start_time_str and end_time_str:
                # Parse timestamps
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

                # Format for display
                start_display = start_time.strftime('%-I:%M%p').lower()
                end_display = end_time.strftime('%-I:%M%p').lower()

                # Calculate duration
                duration = end_time - start_time
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                start_display = "Unknown"
                end_display = "Unknown"
                duration_str = "00:00:00"

            # Extract workout metrics with defaults for missing data
            distance = workout.get('distance', 0)
            steps = workout.get('steps', 0)
            calories = workout.get('calories_burned', 0)
            start_coords = workout.get('start_lat_lng', (0, 0))
            end_coords = workout.get('end_lat_lng', (0, 0))

            # Display workout header with icon
            col1, col2 = st.columns([1, 3])
            with col1:
                # Create circular icon container
                st.markdown("""
                <div style="background-color: #f0f0f0; border-radius: 50%; width: 80px; height: 80px; 
                     display: flex; justify-content: center; align-items: center; margin: 0 auto;">
                    <span style="font-size: 24px;">🏋️</span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Display workout title and time range
                st.markdown(f"<h2 style='margin-bottom: 0;'>Workout {workout_num}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='margin-top: 0;'>{start_display} - {end_display}</p>", unsafe_allow_html=True)

            # Create details container
            st.markdown("""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-top: 10px;">
            """, unsafe_allow_html=True)

            # Details heading
            st.markdown("<h3 style='margin-top: 0;'>Workout Details</h3>", unsafe_allow_html=True)

            # Workout time
            st.markdown("<p><strong>Workout time</strong></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 22px;'>{duration_str}</p>", 
                       unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            # Distance and steps in two columns
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<p><strong>Distance</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 20px;'>{distance:.2f} mi</p>", 
                           unsafe_allow_html=True)

            with col2:
                st.markdown("<p><strong>Total Steps</strong></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 20px;'>{steps:,}</p>", 
                           unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            # Calories
            st.markdown("<p><strong>Total Calories Burned</strong></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 20px;'>{calories} CAL</p>", 
                       unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            # Start and end locations with Folium maps
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<p><strong>Start Location</strong></p>", unsafe_allow_html=True)

                # Create a Folium map for start location
                start_lat, start_lng = start_coords
                start_map = folium.Map(location=[start_lat, start_lng], zoom_start=14)

                # Add a marker for the start position
                folium.Marker(
                    [start_lat, start_lng],
                    popup="Start",
                    icon=folium.Icon(color="green", icon="play"),
                ).add_to(start_map)

                # Display the map with a unique key
                st_folium(start_map, width=300, height=150, key=f"start_map_{workout_id}_{i}", returned_objects=[])

            with col2:
                st.markdown("<p><strong>End Location</strong></p>", unsafe_allow_html=True)

                # Create a Folium map for end location
                end_lat, end_lng = end_coords
                end_map = folium.Map(location=[end_lat, end_lng], zoom_start=14)

                # Add a marker for the end position
                folium.Marker(
                    [end_lat, end_lng],
                    popup="End",
                    icon=folium.Icon(color="red", icon="stop"),
                ).add_to(end_map)

                # Display the map with a unique key
                st_folium(end_map, width=300, height=150, key=f"end_map_{workout_id}_{i}", returned_objects=[])

            # Close the details container
            st.markdown("</div>", unsafe_allow_html=True)

            # Add spacing between workouts
            if i < len(workouts_list) - 1:
                st.markdown("<br>", unsafe_allow_html=True)

        except Exception as e:
            # Handle any unexpected errors
            st.error(f"Error displaying workout {i+1}: {str(e)}")
            continue

    # Update session state to indicate maps have been rendered
    st.session_state.map_rendered = True

def display_activity_page(user_id):
    """
    Displays the activity page for a given user.

    This page includes:
      - All workouts for the user.
      - An overall activity summary.
      - A detailed workout summary with maps
      - A share button to post one of the statistics to the community.
    """
    st.title("Your Activity")

    # Retrieve the user's workouts and profile information.
    workouts = get_user_workouts(user_id)
    user_profile = get_user_profile(user_id)

    if not workouts:
        st.info("No workouts found.")
        return

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Basic Summary", "Detailed Summary with Maps"])
    
    with tab1:
        # Display all workouts.
        st.subheader("All Workouts")
        for workout in workouts:
            #st.markdown(f"**Workout ID:** {workout.get('workout_id', 'N/A')}")
            st.markdown(f"**Start Time:** {workout.get('start_timestamp', 'N/A')}")
            st.markdown(f"**End Time:** {workout.get('end_timestamp', 'N/A')}")
            st.markdown(f"**Distance:** {workout.get('distance', 0)} miles")
            st.markdown(f"**Steps:** {workout.get('steps', 0)}")
            st.markdown(f"**Calories Burned:** {workout.get('calories_burned', 0)} kcal")
            
            st.subheader("➡️ Share This Workout")
            if st.button("Share my step count", key=f"share_{workout.get('workout_id', uuid.uuid4())}"):
                post_content = f"Look at this, I walked {workout.get('steps', 0)} steps today!"
                create_post(user_id, post_content)
            st.markdown("---")

        # Create an overall activity summary.
        st.subheader("Activity Summary")
        total_steps = sum(workout.get('steps', 0) for workout in workouts)
        total_distance = sum(workout.get('distance', 0) for workout in workouts)
        total_calories = sum(workout.get('calories_burned', 0) for workout in workouts)

        st.markdown(f"**Total Steps:** {total_steps}")
        st.markdown(f"**Total Distance:** {total_distance:.2f} miles")
        st.markdown(f"**Total Calories Burned:** {total_calories} kcal")

        # Share button for overall activity summary.
        st.subheader("➡️ Share Your Overall Activity")
        if st.button("Share my overall step count"):
            post_content = f"Look at this, I walked {total_steps} steps today!"
            create_post(user_id, post_content)
    
    with tab2:
        # Display detailed activity summary with maps
        st.subheader("Detailed Workout Analysis")
        display_activity_summary(user_id)

# Example usage:
if __name__ == "__main__":
    # For testing, you can run this page standalone.
    display_activity_page("user2")