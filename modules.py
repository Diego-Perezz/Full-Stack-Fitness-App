#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
import streamlit as st
import pydeck as pdk
from data_fetcher import get_user_workouts, get_user_profile, get_genai_advice, get_user_posts
from datetime import datetime
import folium
from streamlit_folium import st_folium


# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)



def display_post(post_data):
    """
    AI Prompt:
    "Write an AI prompt that would generate the Python function 
    display_post(post_data) which takes a dictionary post_data 
    as input and displays a single post using Streamlit
    
    
    Displays a single post in Streamlit, showing:
    - A circular profile image 
    - The username 
    - The timestamp 
    - The main content
    - A post image
    
    Parameters:
        post_data (dict): A dictionary containing post information
    """
    # Get user profile information for the post author
    try:
        user_id = post_data.get("user_id")
        user_profile = get_user_profile(user_id)
        
        try:
            col1, col2, col3 = st.columns([1,3,1])
        except Exception as e:
            # If layout fails, fallback to a simple display mode
            st.error("⚠️ Layout rendering failed. Falling back to simple display.")
            st.write(f"**{user_profile.get('username', 'Unknown User')}**")
            st.write(post_data.get('timestamp', ''))
            st.write(post_data.get('content', 'No content'))
            
            # Ensure post image is a valid URL before attempting to display it
            post_image = post_data.get('image')
            if post_image and isinstance(post_image, str) and post_image.startswith(("http://", "https://")):
                st.image(post_image, use_column_width=True)
            
            st.markdown("---")  # Separator between posts
            return  # Exit function after fallback layout

        # Profile image section
        with col1:
            user_image = user_profile.get('profile_image', "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png")
            # Check if user_image is a valid URL
            if isinstance(user_image, str) and user_image.startswith(("http://", "https://")):
                st.image(user_image, width=90)
            else:
                st.image("https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png", width=90)
        
        with col2:
            # Display username 
            st.write(f"**{user_profile.get('username', 'Unknown User')}**") 

        with col3:
            # Display timestamp
            st.write(post_data.get('timestamp', ''))

        st.markdown("---")  # Horizontal separator

        # Content section
        st.write(post_data.get('content', 'No content'))

        st.markdown("---")  # Horizontal separator

        # Check if post_image is a valid URL before displaying
        post_image = post_data.get('image')
        if post_image and isinstance(post_image, str) and post_image.startswith(("http://", "https://")):
            st.image(post_image, use_container_width=True)
        
        # Add some space between posts
        st.markdown("<br>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error displaying post: {str(e)}")



def display_activity_summary(workouts_list):
    '''
    Prompt:
        Can you provide the implementation of a display_activity_summary function for a Streamlit 
        app that shows workout details? I need a function that displays workout metrics, 
        timestamps, and uses folium to render start and end location maps for each workout. 
        The function should handle edge cases like missing data and maintain session state.
    '''

    if workouts_list is None or len(workouts_list) == 0:
        st.info("No workout data available.")  # Changed to st.info to match the expected behavior in the test
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



def display_recent_workouts(user_id):
    """Displays a summary of the user's recent workouts."""
    # Fetch workouts
    workouts = get_user_workouts(user_id)

    # Fetch user profile
    user_profile = get_user_profile(user_id)

    # Display user info
    st.sidebar.image(user_profile["profile_image"], width=100)
    st.sidebar.write(f"**{user_profile['full_name']}** (@{user_profile['username']})")

    # Page Title
    st.title("Recent Workouts Summary")

    if not workouts:
        st.write("No workouts available.")
        return

    for workout in workouts:
        #st.subheader(f"Workout ID: {workout['workout_id']}")
        st.write(f"**Start Time:** {workout['start_timestamp']}")
        st.write(f"**End Time:** {workout['end_timestamp']}")
        st.write(f"**Total Distance:** {workout['distance']} km")
        st.write(f"**Total Steps:** {workout['steps']}")
        st.write(f"**Calories Burned:** {workout['calories_burned']} kcal")

        # Unpack start and end coordinates, converting lists to tuples
        start_lat, start_lng = tuple(workout["start_lat_lng"])
        end_lat, end_lng = tuple(workout["end_lat_lng"])

        # Create a Pydeck map with a line connecting start and end points
        workout_map = pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=(start_lat + end_lat) / 2,
                longitude=(start_lng + end_lng) / 2,
                zoom=13,
                pitch=0,
            ),
            layers=[
                # Start & End Points
                pdk.Layer(
                    "ScatterplotLayer",
                    data=[
                        {"lat": start_lat, "lon": start_lng, "color": (0, 255, 0)},  # Green for start
                        {"lat": end_lat, "lon": end_lng, "color": (255, 0, 0)},       # Red for end
                    ],
                    get_position=["lon", "lat"],
                    get_color="color",
                    get_radius=50,
                ),
                # Path Line
                pdk.Layer(
                    "LineLayer",
                    data=[{"start": (start_lng, start_lat), "end": (end_lng, end_lat)}],
                    get_source_position="start",
                    get_target_position="end",
                    get_color=(0, 0, 255),  # Blue Line as a tuple
                    get_width=4,
                ),
            ],
        )

        # Display the map
        st.pydeck_chart(workout_map)

# Streamlit UI

def display_genai_advice(user_id):
    """
    Displays AI-generated advice in an aesthetically pleasing card format.
    
    Parameters:
    -----------
    timestamp : str or None
        The time when the advice was generated
    content : str or None
        The text content of the advice
    image : str or None
        URL to a motivational image (can be None)
    
    Returns:
    --------
    None
    """
    
    '''
    CLAUDE PROMPT:
        Create a Streamlit function called display_genai_advice that shows AI coaching advice in an attractive card format. The function should:

        1. Accept three parameters:
        - timestamp (when the advice was generated)
        - content (the advice text)
        - image (optional URL to a motivational image)

        2. Display the content in a blue bordered card with italic text on the left side

        3. Show the image on the right side or display a emoji if no image is provided

        4. Format the timestamp nicely (like "Aug 15, 2023 at 02:30 PM") with fallbacks for different date formats

        5. Include thorough error handling for all possible edge cases, such as:
        - None values or empty strings for any parameter
        - Invalid timestamp formats
        - Image loading failures
        - Layout rendering problems

        Make sure to implement a fallback simple layout if the layout fails.                           
    '''
    
    advice = get_genai_advice(user_id)
    timestamp = advice.get("timestamp", "")
    content = advice.get("content", "No advice available at this moment.")
    image = advice.get("image", None)
    
    # Input validation
    if timestamp is None:
        timestamp = "Unknown time"
    else:
        timestamp = str(timestamp)  # Ensure timestamp is a string
    
    if content is None:
        content = "No advice available at this moment."
    else:
        content = str(content)  # Ensure content is a string
    
    # Create a card-like container
    with st.container():
        st.markdown("### 🤖 AI Coach Insight")
        
        # Parse and format the timestamp with additional error handling
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            formatted_time = dt.strftime("%b %d, %Y at %I:%M %p")
        except (ValueError, TypeError):
            # Try alternative common formats
            formats_to_try = [
                "%Y-%m-%dT%H:%M:%S",  # ISO format
                "%Y-%m-%dT%H:%M:%S.%f",  # ISO with microseconds
                "%Y/%m/%d %H:%M:%S",
                "%m/%d/%Y %H:%M:%S"
            ]
            
            formatted_time = timestamp  # Default to original string
            for fmt in formats_to_try:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    formatted_time = dt.strftime("%b %d, %Y at %I:%M %p")
                    break
                except (ValueError, TypeError):
                    continue
                
        # Display the timestamp in a subtle way
        st.caption(f"Generated on {formatted_time}")
        
        try:
            # Create columns for better layout
            cols = st.columns([3, 1])
            
            # Left column for advice content
            with cols[0]:
                st.markdown(f"""
                <div style="
                    background-color: #f0f8ff;
                    border-left: 5px solid #4169e1;
                    padding: 15px;
                    border-radius: 15px;
                    font-size: 20px;
                    font-style: italic;
                    margin-bottom: 10px;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    max-height: 400px;
                    overflow-y: auto;">
                    "{content}"
                </div>
                """, unsafe_allow_html=True)
            
            # Right column for image (if available)
            with cols[1]:
                try:
                    if image and isinstance(image, str) and image.strip():
                        st.image(image, use_container_width=True)
                    else:
                        # Display a placeholder or icon when no image
                        st.markdown("""
                        <div style="
                            height: 100%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #4169e1;
                            font-size: 40px;">
                            ✨
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    # Log the error and show fallback
                    print(f"Error displaying image: {str(e)}")
                    
                    st.markdown("""
                    <div style="
                        height: 100%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #FF6347;
                        font-size: 40px;">
                        ❌
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add a subtle divider
            st.markdown("<hr style='margin: 15px 0; opacity: 0.3;'>", unsafe_allow_html=True)
            
        except Exception as e:
            # Fallback to simpler layout if column layout fails
            print(f"Layout error: {str(e)}")
            st.error("Display error occurred. Showing simplified view.")
            st.markdown(f"**{content}**")
            
            # Still try to show image in simplified view
            if image and isinstance(image, str) and image.strip():
                try:
                    st.image(image, width=200)
                except:
                    st.warning("Image could not be displayed")
