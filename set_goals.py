import streamlit as st
from data_fetcher import set_user_nutrition_goals, get_user_nutrition_goals
from datetime import datetime, timedelta

def show(user_id):
    """
    AI Prompt:
    Write a Python function named show that creates a Streamlit page for setting nutrition goals with a user-friendly interface. Fetch any existing goals for the user or use defaults, and create input fields for calorie target, goal type (daily/weekly/monthly), and date range with validation. Include a save button that stores the user's selections and confirms success with a notification.
    """
    
    # Centered title
    st.markdown("<h1 style='text-align: center;'>Goals</h1>", unsafe_allow_html=True)

    # Centered food icon (🍽️ or image)
    st.markdown("<div style='text-align: center; font-size: 125px;'>🍽️</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Get current goals or set defaults
    current_goals = get_user_nutrition_goals(user_id)
    if current_goals:
        default_calorie_goal = current_goals["calorie_target"]
        default_goal_type = current_goals.get("goal_type", "daily")
        default_start_date = current_goals.get("start_date", datetime.now().date())
        default_end_date = current_goals.get("end_date", None)
    else:
        default_calorie_goal = 2000
        default_goal_type = "daily"
        default_start_date = datetime.now().date()
        default_end_date = None

    # Left-aligned Calorie Input
    st.markdown("### Set Calorie Target:")
    calorie_goal = st.number_input("kcal per day", min_value=1000, max_value=5000, value=default_calorie_goal, step=50)
    
    # Goal type selection
    st.markdown("### Goal Type:")
    goal_type = st.selectbox(
        "Select goal type", 
        options=["daily", "weekly", "monthly"], 
        index=["daily", "weekly", "monthly"].index(default_goal_type)
    )
    
    # Date range selection
    st.markdown("### Goal Duration:")
    
    # Start date with min date validation
    min_date = datetime.now().date() - timedelta(days=30)  # Allow setting goals up to 30 days in the past
    start_date = st.date_input(
        "Start date", 
        value=default_start_date,
        min_value=min_date
    )
    
    # End date - can be None for ongoing goals
    has_end_date = st.checkbox("Set end date", value=default_end_date is not None)
    end_date = None
    if has_end_date:
        end_date = st.date_input(
            "End date", 
            value=default_end_date if default_end_date else (start_date + timedelta(days=30)),
            min_value=start_date
        )
        
        # Validate end date is after start date
        if end_date < start_date:
            st.error("End date must be after start date.")
            return
    
    # Save button
    st.subheader("")
    # Centered and styled Save button
    if st.button("Save"):
        set_user_nutrition_goals(user_id, calorie_goal, goal_type, start_date, end_date)
        st.success("Goals saved!")

