import streamlit as st
import datetime
from modules import display_genai_advice, display_recent_workouts
from activity_page import display_activity_page
from community_page import display_posts_page
from dateutil import parser
from modules import display_genai_advice, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_workouts, get_users, get_workout_stats, get_user_water_intake, get_nutrition_data, get_meal_details
from water_page import display_water_intake_page  # Import the water intake page module
from nutrition_analytics import display_nutrition_analytics_page
from meal_logger import display_meal_logger_page
from nutrition_goals_tracker import show as display_nutrition_goals_tracker
from set_goals import show as display_set_goals_page


st.set_page_config(
    page_title="Social Fitness App",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None  # Hide the default menu
)

# Hide deployment info, made with streamlit messages, and other technical details
# through custom CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Hide data caching and spinner notifications */
    div[data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    
    /* Hide any warning and info boxes unless explicitly created by our app */
    .element-container:has(div[data-testid="stInfoBox"]:not(.custom-info)) {
        display: none;
    }
    
    /* Ensure the main header is at the top where it belongs */
    .main-header {
        font-size: 42px;
        font-weight: bold;
        margin-top: 0 !important;
        margin-bottom: 10px;
        color: #1E88E5;
    }
    
    /* Rest of custom styling */
    .feature-card {
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #1E88E5;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .feature-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #1E88E5;
    }
    /* Navbar styling */
    .navbar-container {
       
        width: 100%;
        margin-bottom: 20px;
    }
    /* Remove default column padding and gaps */
    .row-widget.stHorizontal {
        gap: 0 !important;
        padding: 0 !important;
    }
    /* Override Streamlit's default button styles */
    .stButton > button {
        font-weight: 500;
        border-radius: 0 !important;
        padding: 0.75rem 0.5rem !important;
        border: none !important;
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
    }
    /* Style for the navigation buttons */
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    .stButton > button[data-testid="baseButton-secondary"] {
        color: #1E88E5 !important;
        background-color: #f8f9fa !important;
    }
    /* Fix for emoji spacing in buttons */
    .stButton button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .welcome-message {
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
    }
    .section-divider {
        margin: 30px 0;
        border-top: 1px solid #eee;
    }
    
    div.block-container {
        padding-top: 25px !important;
    }
</style>
""", unsafe_allow_html=True)

# Add caching to improve performance
@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_user_profile(user_id):
    return get_user_profile(user_id)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_user_posts(user_id):
    return get_user_posts(user_id)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_user_workouts(user_id):
    return get_user_workouts(user_id)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_genai_advice(user_id):
    return get_genai_advice(user_id)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_user_water_intake(user_id, date):
    return get_user_water_intake(user_id, date)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_nutrition_data(user_id, days=1):
    return get_nutrition_data(user_id, days)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_meal_details(user_id, days=1):
    return get_meal_details(user_id, days)

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def cached_get_users():
    return get_users()

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Default user ID - could be made selectable in the future
DEFAULT_USER_ID = 'user1'

def create_navbar():
    '''
    CLAUDE Prompt:
        Create a Streamlit navigation function that:

            1. Is named create_navbar()
            2. Creates a horizontal navbar with 6 items: Home, Profile, Posts, Workouts, Activity, and AI Advice (each with an emoji)
            3. Makes the navbar full width using a custom container
            4. Adds buttons that:
                - Fill their container width
                - Show active page in primary color
                - Store selected page in session state
                - Trigger page refresh when clicked
    '''
    # """Create a navigation bar for the app"""
    nav_items = {
        'home': '🏠 Home',
        'profile': '👤 Profile',
        'posts': '📝 Posts',
        'workouts': '🏋️ Workouts',
        'activity': '📊 Activity',
        'water': '💧 Water',
        'meals': '🍽️ Meals',
        'goals': '🎯 Goals',
        'nutrition': '🍎 Analytics',
        'advice': '🤖 AI Advice'
    }
    
    # Create a container with full width for the navbar
    st.markdown('<div class="navbar-container"></div>', unsafe_allow_html=True)
    
    # Create columns with no gap between them
    cols = st.columns(len(nav_items), gap="small")
    
    # Add buttons that fill each column
    for i, (key, label) in enumerate(nav_items.items()):
        with cols[i]:
            if st.button(
                label, 
                key=f"nav_{key}", 
                use_container_width=True,
                type="primary" if st.session_state.page == key else "secondary"
            ):
                st.session_state.page = key
                st.rerun()




def display_home_page(user_id=DEFAULT_USER_ID):
    '''
    Display the main homepage with previews of all features
    '''
    try:
        # First, create a container for the welcome header that will appear at the top
        welcome_container = st.container()
        
        # Then create the main content container
        main_content = st.container()
        
        # Inside the main content container, create the layout
        with main_content:
            # Main dashboard in a 2x3 grid layout
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Recent workout summary placeholder
                st.markdown("<div class='feature-card'>📊 Recent Activity</div>", unsafe_allow_html=True)
                workout_container = st.container()
                
                # Water intake preview placeholder
                st.markdown("<div class='feature-card'>💧 Water Intake</div>", unsafe_allow_html=True)
                water_container = st.container()
                
            with col2:
                # Nutrition preview placeholder
                st.markdown("<div class='feature-card'>🍽️ Today's Nutrition</div>", unsafe_allow_html=True)
                nutrition_container = st.container()
                
                # Recent post preview placeholder
                st.markdown("<div class='feature-card'> 📝 Recent Post</div>", unsafe_allow_html=True)
                post_container = st.container()
                
            with col3:
                # AI Advice preview placeholder
                st.markdown("<div class='feature-card'> 🤖 AI Coach Says</div>", unsafe_allow_html=True)
                advice_container = st.container()
                
                # Friends activity preview placeholder
                st.markdown("<div class='feature-card'> 👥 Friends</div>", unsafe_allow_html=True)
                friends_container = st.container()
        
        # Load user profile data
        try:
            user_profile = cached_get_user_profile(user_id)
        except Exception as e:
            print(f"Error loading user profile: {str(e)}")
            user_profile = None
        
        # Now populate the welcome container at the top
        with welcome_container:
            if user_profile:
                st.markdown(f"<div class='main-header'>Welcome to Social Fitness, {user_profile.get('full_name', 'User')}!</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='main-header'>Welcome to Social Fitness!</div>", unsafe_allow_html=True)
            st.markdown("<div class='welcome-message'>Track your workouts, connect with friends, and get AI-powered fitness advice.</div>", unsafe_allow_html=True)
            
        # Now populate the various content containers
        # Using the containers we created earlier ensures the content appears in the right sections
        
        # Populate workout container
        with workout_container:
            try:
                st.markdown("<div class='feature-title'>", unsafe_allow_html=True)
                
                # Get user data - using cached versions for better performance
                user_workouts = cached_get_user_workouts(user_id)
                
                if user_workouts and len(user_workouts) > 0:
                    workout = user_workouts[0]  # Show first workout
                    st.write(f"**Last workout:** {workout.get('start_timestamp', 'N/A')}")
                    st.write(f"📏 Distance: {workout.get('distance', 0)} miles")
                    st.write(f"👣 Steps: {workout.get('steps', 0)}")
                    st.write(f"🔥 Calories: {workout.get('calories_burned', 0)}")

                    if st.button("See All Workouts", key="home_workouts"):
                        st.session_state.page = 'workouts'
                        st.rerun()
                else:
                    st.write("No recent workouts found.")
                    
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Error loading workout data: {str(e)}")
                st.write("Activity data currently unavailable.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Get water intake data for today and populate container
        with water_container:
            try:
                st.markdown("<div class='feature-title'>", unsafe_allow_html=True)
                
                today = datetime.datetime.now().date()
                today_water_intake = cached_get_user_water_intake(user_id, today)
                total_water_ml = sum(record['amount_ml'] for record in today_water_intake)
                water_percentage = min(100, int((total_water_ml / 2000) * 100))  # 2000ml recommended daily intake
                
                st.write(f"**Today's intake:** {total_water_ml} ml")
                st.progress(water_percentage / 100)
                st.write(f"{water_percentage}% of daily goal")
                
                if st.button("Track Water", key="home_water"):
                    st.session_state.page = 'water'
                    st.rerun()
                    
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Error loading water intake data: {str(e)}")
                st.write("Water intake data currently unavailable.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Populate nutrition container
        with nutrition_container:
            try:
                st.markdown("<div class='feature-title'>", unsafe_allow_html=True)
                
                # Get nutrition data and meals
                today = datetime.datetime.now().date()
                nutrition_data = cached_get_nutrition_data(user_id, days=1)
                today_nutrition = next((item for item in nutrition_data if item['date'] == today.strftime('%Y-%m-%d')), None)
                
                if today_nutrition:
                    # Calculate percentages for macros
                    total_macros = today_nutrition.get('total_protein', 0) + today_nutrition.get('total_carbs', 0) + today_nutrition.get('total_fat', 0)
                    
                    if total_macros > 0:
                        protein_pct = int((today_nutrition.get('total_protein', 0) / total_macros) * 100)
                        carbs_pct = int((today_nutrition.get('total_carbs', 0) / total_macros) * 100)
                        fat_pct = int((today_nutrition.get('total_fat', 0) / total_macros) * 100)
                        
                        st.write(f"**Calories:** {today_nutrition.get('total_calories', 0):.0f}")
                        st.write(f"**Macros:** P: {protein_pct}% | C: {carbs_pct}% | F: {fat_pct}%")
                        
                        # Show recent meal only if we have nutrition data
                        recent_meals = cached_get_meal_details(user_id, days=1)
                        if recent_meals:
                            meal = recent_meals[0]  # Show most recent meal
                            meal_time = datetime.datetime.fromisoformat(meal.get('meal_time')).strftime('%I:%M %p')
                            st.write(f"**Last meal:** {meal_time} - {meal.get('food_name', 'Unknown')}")
                    else:
                        st.write("No nutrition data recorded today.")
                else:
                    st.write("No nutrition data recorded today.")
                    
                if st.button("Log Meal", key="home_meal"):
                    st.session_state.page = 'meals'
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Error loading nutrition data: {str(e)}")
                st.write("Nutrition data currently unavailable.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Populate posts container
        with post_container:
            try:
                st.markdown("<div class='feature-title'>", unsafe_allow_html=True)
                
                user_posts = cached_get_user_posts(user_id)
                
                if user_posts and len(user_posts) > 0:
                    post = user_posts[0]  # Show first post
                    st.write(f"**Posted on:** {post.get('timestamp', 'Unknown time')}")
                    st.write(post.get('content', 'No content available'))
                    if st.button("See All Posts", key="home_posts"):
                        st.session_state.page = 'posts'
                        st.rerun()
                else:
                    st.write("No recent posts found.")
                
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Error loading posts: {str(e)}")
                st.write("Posts currently unavailable.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Populate advice container
        with advice_container:
            try:
                st.markdown("<div class='feature-title'>", unsafe_allow_html=True)
                
                ai_advice = cached_get_genai_advice(user_id)
                
                if ai_advice:
                    st.write(ai_advice.get('content', 'No advice available at the moment.'))
                else:
                    st.write("No AI advice available.")
                    
                if st.button("Get More Advice", key="home_advice"):
                    st.session_state.page = 'advice'
                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Error loading AI advice: {str(e)}")
                st.write("AI advice currently unavailable.")
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Populate friends container
        with friends_container:
            try:
                st.markdown("<div class='feature-title'>", unsafe_allow_html=True)
                
                friends = user_profile.get('friends', []) if user_profile else []
                
                if friends:
                    friend_list = []
                    # Limit to 3 friends to reduce API calls
                    for friend_id in friends[:3]:
                        try:
                            friend = cached_get_user_profile(friend_id)
                            friend_list.append(f"- **{friend.get('full_name', 'Unknown')}** (@{friend.get('username', 'unknown')})")
                        except Exception as e:
                            print(f"Error loading friend {friend_id}: {str(e)}")
                            friend_list.append(f"- Friend unavailable")
                    
                    if len(friends) > 3:
                        friend_list.append(f"...and {len(friends) - 3} more")
                        
                    if friend_list:
                        st.markdown("\n".join(friend_list))
                    else:
                        st.write("Could not load friends data.")
                    
                    if st.button("View Profile", key="home_profile"):
                        st.session_state.page = 'profile'
                        st.rerun()
                else:
                    st.write("No friends added yet.")
                
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                print(f"Error loading friends: {str(e)}")
                st.write("Friends list currently unavailable.")
                st.markdown("</div>", unsafe_allow_html=True)
            
    except Exception as e:
        # General error handling for the entire page
        print(f"Error loading homepage: {str(e)}")
        # Display friendly message without technical details
        st.info("Some content couldn't be loaded. Please refresh or try again later.")

def display_profile_page(user_id=DEFAULT_USER_ID):
    try:
        user_profile = get_user_profile(user_id)

        # --- Profile Header ---
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(user_profile.get('profile_image', ''), width=200)

        with col2:
            st.title(user_profile.get('full_name', 'User'))
            st.subheader(f"@{user_profile.get('username', 'username')}")
            st.write(f"**Birthday:** {user_profile.get('date_of_birth', 'Not available')}")
            friends = user_profile.get('friends', [])
            st.write(f"**Friends:** {len(friends)}")

        # --- Activity Stats ---
        st.markdown("---")
        st.subheader("📊 Activity Statistics")
        workouts = get_user_workouts(user_id)

        if workouts:
            total_distance = sum(w.get('distance', 0) for w in workouts)
            total_steps = sum(w.get('steps', 0) for w in workouts)
            total_calories = sum(w.get('calories_burned', 0) for w in workouts)

            stat1, stat2, stat3 = st.columns(3)
            stat1.metric("🏃 Total Distance", f"{total_distance:.1f} miles")
            stat2.metric("👣 Total Steps", f"{total_steps:,}")
            stat3.metric("🔥 Total Calories", f"{total_calories:,}")

            # --- Streak Stats ---
            stats = get_workout_stats(user_id)

            st.markdown("### 🔥 Workout Streak")
            st.markdown(f"**{stats['currentStreak']} days in a row**")

            # Weekday tracker (highlight active days)
            workout_days = set()
            for workout in workouts:
                try:
                    dt = parser.parse(workout['start_timestamp'])
                    workout_days.add(dt.weekday())  # Monday = 0, Sunday = 6
                except Exception as e:
                    st.warning(f"Skipping invalid timestamp: {workout.get('start_timestamp', '')}")

            day_labels = ["M", "T", "W", "Th", "F", "Sa", "Su"]
            day_cols = st.columns(7)

            for i, col in enumerate(day_cols):
                with col:
                    if i in workout_days:
                        st.markdown(f"### 🟢 **{day_labels[i]}**")  # Active day
                    else:
                        st.markdown(f"### ⚪ {day_labels[i]}")       # Inactive day

            # --- Achievements Section ---
            st.subheader("🏅 Achievements")

            all_badges = [
            # Streak badges
            { "label": "🔥 3‑Day Streak",     "earned": "3-Day Streak"     in stats["badgeList"] },
            { "label": "🔥 7‑Day Streak",     "earned": "7-Day Streak"     in stats["badgeList"] },
            { "label": "💥 14‑Day Warrior",   "earned": "14‑Day Warrior"   in stats["badgeList"] },
            { "label": "🚀 30‑Day Beast",     "earned": "30‑Day Beast"     in stats["badgeList"] },

            # Workout‑count badges
            { "label": "🎯 10 Workouts Complete",  "earned": "10 Workouts Complete"  in stats["badgeList"] },
            { "label": "🏆 50 Workouts Legend",    "earned": "50 Workouts Legend"    in stats["badgeList"] },

            # Step‑distance badges
            { "label": "👣 Walked a 5k",            "earned": "Walked a 5k"            in stats["badgeList"] },
            { "label": "👟 Walked a 10k",           "earned": "Walked a 10k"           in stats["badgeList"] },
            { "label": "🚶 Walked a 15k",           "earned": "Walked a 15k"           in stats["badgeList"] },
            { "label": "🏅 Walked a Half‑Marathon", "earned": "Walked a Half-Marathon" in stats["badgeList"] },
            { "label": "🏅 Walked a Marathon",      "earned": "Walked a Marathon"      in stats["badgeList"] },
            ]

            badge_cols = st.columns(3)
            for i, badge in enumerate(all_badges):
                with badge_cols[i % 3]:
                    if badge["earned"]:
                        if badge.get("action"):
                            if st.button(badge["label"]):
                                st.session_state.page = badge["action"]
                        else:
                            st.success(badge["label"])
                    else:
                        st.caption(f"🔒 {badge['label']}")

            # --- 30-Day Streak Progress
            st.subheader("📈 30 Day Streak Progress")
            progress = min(stats["currentStreak"], 30)
            percent = int((progress / 30) * 100)
            st.progress(progress / 30)
            st.write(f"**{progress} of 30 Days Completed ({percent}%)**")

        else:
            st.info("No workout data available to show statistics.")

        # --- Friends Section ---
        st.markdown("---")
        st.subheader("👥 Friends")
        if friends:
            friend_cols = st.columns(min(3, len(friends)))
            for i, friend_id in enumerate(friends):
                try:
                    friend = get_user_profile(friend_id)
                    with friend_cols[i % 3]:
                        st.image(friend.get('profile_image', ''), width=100)
                        st.write(f"**{friend.get('full_name', 'Friend')}**")
                        st.write(f"@{friend.get('username', '')}")
                except:
                    with friend_cols[i % 3]:
                        st.write(f"Friend {i+1} data unavailable")
        else:
            st.info("No friends added yet.")

    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")



def display_workouts_page(user_id=DEFAULT_USER_ID):
    """Display recent workouts summary"""
    st.title("Recent Workouts")
    st.write("Here's a summary of your recent workouts:")
    
    try:
        # Pass user_id, not get_user_workouts(user_id)
        display_recent_workouts(user_id)
    except Exception as e:
        st.error(f"Error displaying workouts: {str(e)}")





def display_activity_page_wrapper(user_id=DEFAULT_USER_ID):
    """Display activity page wrapper"""
    try:
        # Call the actual activity page function
        display_activity_page(user_id)
    except Exception as e:
        st.error(f"Error displaying activity page: {str(e)}")




def display_advice_page(user_id=DEFAULT_USER_ID):
    '''
    CLAUDE Prompt:
    Create a Streamlit function that:

        1. Displays an AI fitness coach page with title and description
        2. Fetches and shows personalized advice using the display_genai_advice function
        3. Adds an interactive Q&A section where users can ask fitness questions
        4. Simulates AI responses using random pre written messages
        5. Includes appropriate feedback messages and error handling
    '''
    
    # """Display AI-generated fitness advice"""
    st.title("AI Fitness Coach")
    st.write("Get personalized advice based on your workout data:")
    
    try:
        # Display the advice
        display_genai_advice(user_id)
        
    except Exception as e:
        st.error(f"Error displaying AI advice: {str(e)}")

def display_goals_page(user_id=DEFAULT_USER_ID):
    """Display the nutrition goals tracking page"""
    display_nutrition_goals_tracker(user_id)

def display_set_goals_page_wrapper(user_id=DEFAULT_USER_ID):
    """Display the set goals page"""
    display_set_goals_page(user_id)

def main():
    '''
    Main function for the Streamlit app that:
    1. Displays a sidebar with app logo, title, and user selector dropdown
    2. Displays a navigation bar
    3. Routes to different pages based on session_state.page value
    4. Handles 6 different page types (home, profile, posts, workouts, activity, advice)
    5. Includes copyright information in the sidebar footer
    '''
    # Fetch users from the database (replace with real query to your database)
    users = cached_get_users()

    # Sidebar setup
    with st.sidebar:
        st.title("Social Fitness App")
        st.write("Connect, Track, Improve!")
        
        # In a real app, you would have user authentication here
        # For now, we'll use a dropdown to select different users from the database
        user_options = {user['UserId']: f"{user['Name']} (@{user['Username']})" for user in users}
        selected_user = st.selectbox(
            "View as User:",
            options=list(user_options.keys()),
            format_func=lambda x: user_options[x]
        )

        # Store selected user in session state
        st.session_state.selected_user = selected_user
        
        st.markdown("---")
        st.caption("© 2025 Social Fitness App")
    
    # Create the navbar
    create_navbar()

    # Display the appropriate page based on session state
    if st.session_state.page == 'home':
        display_home_page(st.session_state.selected_user)
    elif st.session_state.page == 'profile':
        display_profile_page(st.session_state.selected_user)
    elif st.session_state.page == 'posts':
        display_posts_page(st.session_state.selected_user)
    elif st.session_state.page == 'workouts':
        display_workouts_page(st.session_state.selected_user)
    elif st.session_state.page == 'activity':
        display_activity_page_wrapper(st.session_state.selected_user)
    elif st.session_state.page == 'water':
        display_water_intake_page(st.session_state.selected_user)
    elif st.session_state.page == 'meals':
        display_meal_logger_page(st.session_state.selected_user)
    elif st.session_state.page == 'nutrition':
        display_nutrition_analytics_page(st.session_state.selected_user)
    elif st.session_state.page == 'advice':
        display_advice_page(st.session_state.selected_user)
    elif st.session_state.page == 'goals':
        display_goals_page(st.session_state.selected_user)
    elif st.session_state.page == 'set_goals':
        display_set_goals_page_wrapper(st.session_state.selected_user)


# This is the starting point for your app
if __name__ == '__main__':
    main()
