import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from data_fetcher import get_user_nutrition_goals, get_daily_nutrition_progress, get_weekly_nutrition_progress

def show(user_id):
    """
    Display the nutrition goals tracking page
    
    Args:
        user_id (str): Current user ID
    """
    
    """
    AI Prompt:
    Write a Python function named show that displays a nutrition goals tracking page in Streamlit for a given user. Fetch the user's nutrition goals and create tabs for daily and weekly views, displaying a warning and goal-setting button if no goals exist. Include a button at the bottom to edit goals that updates the session state to navigate to the goals setting page.
    """
    
    st.title("🎯 Nutrition Goals Tracker")
    
    # Get user goals
    goals = get_user_nutrition_goals(user_id)
    
    if not goals:
        st.warning("You haven't set any calorie goals yet. Please set your goals first.")
        st.button("Set Goals", on_click=lambda: st.session_state.update({"page": "set_goals"}))
        return
        
    # Create tabs for daily and weekly views
    tab1, tab2 = st.tabs(["Daily Progress", "Weekly Trends"])
    
    with tab1:
        display_daily_progress(user_id, goals)
        
    with tab2:
        display_weekly_trends(user_id, goals)
        
    # Add button to set/edit goals
    st.divider()
    st.button("Edit Goals", on_click=lambda: st.session_state.update({"page": "set_goals"}))

def display_daily_progress(user_id, goals):
    """
    Display daily nutrition progress against goals
    
    Args:
        user_id (str): User ID
        goals (dict): User nutrition goals
    """
    
    """
    AI Prompt:
    Write a Python function named display_daily_progress that visualizes a user's daily nutrition progress compared to their goals using Streamlit. Create a date selector, fetch nutrition progress for the selected date, and display calorie metrics including goal, consumed, remaining, and status indicators with appropriate styling. Include a progress bar and display goal information including type, start date, and end date.
    """
    
    # Date selector
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_date = st.date_input("Select Date", datetime.now())
    
    # Get daily progress
    date_str = selected_date.strftime("%Y-%m-%d")
    progress = get_daily_nutrition_progress(user_id, date_str)
    
    if not progress:
        st.info(f"No nutrition data available for {date_str}")
        return
    
    # Display calories summary
    st.subheader("Calories")
    
    # Create columns for metrics
    cols = st.columns(4)
    
    # Display calorie metrics
    with cols[0]:
        st.metric(
            "Calories Goal", 
            f"{goals['calorie_target']} kcal",
            help=f"Your {goals['goal_type']} calorie target"
        )
    
    with cols[1]:
        st.metric(
            "Consumed", 
            f"{int(progress['consumption']['calories'])} kcal",
            f"{int(progress['progress']['calories_percent'])}%" if progress['progress'].get('calories_percent', 0) > 0 else "0%",
            help="Total calories consumed today"
        )
    
    with cols[2]:
        st.metric(
            "Remaining", 
            f"{int(progress['remaining']['calories'])} kcal",
            help="Calories left to consume today"
        )
        
    with cols[3]:
        # Calculate status based on percentage of goal
        percent_of_goal = progress['progress'].get('calories_percent', 0)
        if percent_of_goal > 100:
            status = "⚠️ Over Goal"
            color = "red"
        elif percent_of_goal > 90:
            status = "✅ On Target"
            color = "green"
        elif percent_of_goal > 70:
            status = "👍 Good Progress"
            color = "blue"
        else:
            status = "🔄 In Progress"
            color = "gray"
            
        st.markdown(f"<h3 style='color: {color}; font-size: 1.2em;'>{status}</h3>", unsafe_allow_html=True)
    
    # Calorie progress bar
    st.progress(progress['progress']['calories_percent'] / 100 if progress['progress'].get('calories_percent', 0) <= 100 else 1.0)
    
    # Goal type and dates information
    st.subheader("Goal Information")
    
    # Create columns for goal info
    info_cols = st.columns(3)
    
    with info_cols[0]:
        st.markdown(f"**Goal Type:** {goals['goal_type'].capitalize()}")
    
    with info_cols[1]:
        st.markdown(f"**Start Date:** {goals['start_date'].strftime('%Y-%m-%d')}")
    
    with info_cols[2]:
        if goals['end_date']:
            st.markdown(f"**End Date:** {goals['end_date'].strftime('%Y-%m-%d')}")
        else:
            st.markdown("**End Date:** Ongoing")
            
    # Add updated timestamp if available
    if 'updated_at' in progress:
        st.caption(f"Last updated: {progress['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}")

def display_weekly_trends(user_id, goals):
    """
    Display weekly nutrition trends
    
    Args:
        user_id (str): User ID
        goals (dict): User nutrition goals
    """
    
    """
    AI Prompt:
    Write a Python function named display_weekly_trends that visualizes a user's weekly nutrition data using Streamlit and Plotly. Create a slider for selecting the number of days to display, fetch weekly progress data, and show metrics for average calories consumed and remaining. Generate two interactive charts: a bar chart comparing daily calories to the target, and a line chart showing the percentage of calorie goal achieved each day.
    """
    
    # Get weekly progress data
    days_selector = st.slider("Number of days", min_value=3, max_value=30, value=7, step=1)
    weekly_progress = get_weekly_nutrition_progress(user_id, days=days_selector)
    
    if not weekly_progress or not weekly_progress.get("daily_progress"):
        st.info(f"No nutrition data available for the last {days_selector} days")
        return
    
    # Display weekly averages
    st.subheader("Weekly Averages")
    
    # Create columns for metrics
    cols = st.columns(2)
    
    # Display calorie metrics
    with cols[0]:
        avg_calories = weekly_progress["averages"]["calories"]
        calories_target = goals["calorie_target"]
        st.metric(
            "Avg. Calories", 
            f"{int(avg_calories)} kcal",
            f"{int((avg_calories / calories_target) * 100)}% of goal" if calories_target > 0 else "No goal set",
            help=f"Daily average over {days_selector} days"
        )
    
    # Display remaining calories metrics
    with cols[1]:
        avg_remaining = weekly_progress["averages"].get("calories_remaining", 0)
        st.metric(
            "Avg. Remaining", 
            f"{int(avg_remaining)} kcal",
            help=f"Average daily calories remaining over {days_selector} days"
        )
    
    # Create daily calorie trend chart
    st.subheader("Daily Calorie Trend")
    
    # Extract dates and calories
    daily_data = weekly_progress["daily_progress"]
    
    # Convert to DataFrame for the chart
    df = pd.DataFrame([{
        'date': day["date"], 
        'calories': day["consumption"]["calories"],
        'target': goals["calorie_target"]
    } for day in daily_data])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create figure with secondary y-axis
    fig = px.bar(
        df, 
        x='date', 
        y='calories',
        text=df['calories'].apply(lambda x: f'{int(x)}')
    )
    
    # Add target line
    fig.add_trace(
        go.Scatter(
            x=df['date'], 
            y=[goals["calorie_target"]] * len(df),
            mode='lines',
            name=f'{goals["goal_type"].capitalize()} Target',
            line=dict(color='red', width=2, dash='dash')
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Daily Calories vs Target',
        xaxis_title='Date',
        yaxis_title='Calories (kcal)',
        legend_title='Legend',
        barmode='group',
        height=400
    )
    
    # Show chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Progress Percentage Trend
    st.subheader("Daily Progress Percentage")
    
    # Calculate percentage of goal
    df['percentage'] = (df['calories'] / df['target'] * 100).clip(upper=100)
    
    # Create percentage chart
    fig_pct = px.line(
        df, 
        x='date', 
        y='percentage',
        markers=True
    )
    
    # Add 100% line
    fig_pct.add_trace(
        go.Scatter(
            x=df['date'], 
            y=[100] * len(df),
            mode='lines',
            name='100% Goal',
            line=dict(color='green', width=1, dash='dash')
        )
    )
    
    # Update layout
    fig_pct.update_layout(
        title='Daily Percentage of Calorie Goal',
        xaxis_title='Date',
        yaxis_title='Percentage (%)',
        legend_title='Legend',
        height=400
    )
    
    # Update y-axis
    fig_pct.update_yaxes(range=[0, 110])
    
    # Show chart
    st.plotly_chart(fig_pct, use_container_width=True) 