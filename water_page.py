import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import altair as alt
from data_fetcher import get_user_water_intake, add_water_intake, get_daily_water_summary

# Define the recommended daily water intake in ml (2000ml = 2 liters)
RECOMMENDED_DAILY_INTAKE = 2000


def display_water_intake_page(user_id):
    """
    Display the water intake tracking page
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function named display_water_intake_page that creates a water intake tracking interface in Streamlit for a specified user. Create a title for the page and implement a tabbed interface with two tabs labeled "Today's Intake" and "Weekly Summary". Call separate functions to display today's water intake data and weekly summary data in their respective tabs.
    """
    
    st.title("💧 Water Intake Tracker")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Today's Intake", "Weekly Summary"])
    
    with tab1:
        display_todays_intake(user_id)
    
    with tab2:
        display_weekly_summary(user_id)


def display_todays_intake(user_id):
    """
    Display and manage today's water intake
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function named display_todays_intake that creates an interactive Streamlit interface for tracking today's water intake for a specified user. Fetch and display the user's current water intake with a progress bar and percentage toward the daily recommendation, then implement quick-add buttons for common amounts and a custom form for specific entries. Display a formatted table of today's water log with styled CSS and a download option.
    """
    
    today = datetime.datetime.now().date()
    today_str = today.strftime("%A, %B %d")
    
    st.header(f"Today's Water Intake ({today_str})")
    
    # Get today's water intake data
    today_intake = get_user_water_intake(user_id, today)
    
    # Calculate total intake for today
    total_ml = sum(record['amount_ml'] for record in today_intake)
    percentage = min(100, int((total_ml / RECOMMENDED_DAILY_INTAKE) * 100))
    
    # Display progress bar and stats
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Progress")
        st.progress(percentage / 100)
        st.write(f"**{total_ml} ml** of {RECOMMENDED_DAILY_INTAKE} ml recommended daily intake ({percentage}%)")
    
    with col2:
        st.subheader("Quick Add")
        
        # Common water intake amounts
        amounts = {
            "Small Glass (200ml)": 200,
            "Medium Glass (300ml)": 300,
            "Large Glass (400ml)": 400,
            "Water Bottle (500ml)": 500,
            "Large Bottle (1000ml)": 1000
        }
        
        selected_amount = st.selectbox("Amount", list(amounts.keys()))
        
        if st.button("Add Water"):
            if add_water_intake(user_id, amounts[selected_amount]):
                st.success(f"Added {amounts[selected_amount]} ml of water!")
                # Rerun the app to show the updated data
                st.rerun()
            else:
                st.error("Failed to add water intake. Please try again.")
    
    # Custom water intake form
    st.subheader("Custom Water Intake")
    
    with st.form("custom_water_form"):
        custom_amount = st.number_input("Amount (ml)", min_value=10, max_value=5000, value=250, step=50)
        col1, col2 = st.columns(2)
        
        with col1:
            custom_date = st.date_input("Date", value=today, max_value=today)
        
        with col2:
            custom_time = st.time_input("Time", value=datetime.datetime.now().time())
        
        # Combine date and time into a datetime object
        custom_datetime = datetime.datetime.combine(custom_date, custom_time)
        
        submitted = st.form_submit_button("Add Custom Entry")
        if submitted:
            if add_water_intake(user_id, custom_amount, custom_datetime):
                st.success(f"Added {custom_amount} ml of water!")
                # Rerun the app to show the updated data
                st.rerun()
            else:
                st.error("Failed to add water intake. Please try again.")
    
    # Display today's water intake log
    st.subheader("Today's Water Log")
    
    if today_intake:
        # Create a DataFrame for better display
        df = pd.DataFrame(today_intake)
        df['intake_time'] = pd.to_datetime(df['intake_time']).dt.strftime('%I:%M %p')
        df = df.rename(columns={
            'amount_ml': 'Amount (ml)',
            'intake_time': 'Time'
        })
        
        # Keep only the columns we want to display
        df = df[['Time', 'Amount (ml)']]
        
        # Apply custom CSS to make the table larger and more prominent
        custom_css = """
        <style>
        .dataframe {
            width: 100% !important;
            font-size: 18px !important;
            margin-bottom: 30px !important;
        }
        .dataframe th {
            background-color: #1E88E5 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 12px 15px !important;
            text-align: left !important;
        }
        .dataframe td {
            padding: 12px 15px !important;
            text-align: left !important;
            border-bottom: 1px solid #ddd !important;
        }
        .dataframe tr:hover {
            background-color: #f5f5f5 !important;
        }
        </style>
        """
        
        # Display the table without index column using HTML with custom CSS
        st.markdown(custom_css, unsafe_allow_html=True)
        st.markdown(
            df.to_html(index=False, classes='dataframe'),
            unsafe_allow_html=True
        )
        
        # Add option to download the data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Water Log",
            data=csv,
            file_name="water_intake_log.csv",
            mime="text/csv",
        )
    else:
        st.info("No water intake recorded today. Add your first entry!")


def display_weekly_summary(user_id):
    """
    Display a summary of the user's water intake over the past week
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function named display_weekly_summary that creates a visual summary of a user's water intake over the past 7 days using Streamlit and Altair. Fetch the daily water summary data, create an interactive bar chart with color-coded bars based on meeting the recommended intake target, and display key statistics including total weekly intake, daily average, and days the target was met. Add personalized hydration tips based on the user's average water intake performance compared to the recommended amount.
    """
    
    st.header("Weekly Water Intake Summary")
    
    # Get summary data for the past 7 days
    summary_data = get_daily_water_summary(user_id, days=7)
    
    if not summary_data:
        st.info("No water intake data available for the past week.")
        return
    
    # Create a DataFrame for the chart
    df = pd.DataFrame(summary_data)
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.strftime('%a')
    
    # Create the bar chart using Altair
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('day:O', title='Day'),
        y=alt.Y('total_ml:Q', title='Water Intake (ml)'),
        color=alt.condition(
            alt.datum.total_ml >= RECOMMENDED_DAILY_INTAKE,
            alt.value('#1E88E5'),  # Blue for meeting the goal
            alt.value('#FFB300')   # Orange for not meeting the goal
        ),
        tooltip=['day:O', 'total_ml:Q']
    ).properties(
        title='Daily Water Intake (Past 7 Days)',
        width=600
    )
    
    # Add a horizontal line for the daily recommendation
    rule = alt.Chart(pd.DataFrame({'recommended': [RECOMMENDED_DAILY_INTAKE]})).mark_rule(
        color='red',
        strokeDash=[10, 10]
    ).encode(
        y='recommended:Q'
    )
    
    # Display the chart
    st.altair_chart(chart + rule, use_container_width=True)
    
    # Calculate statistics
    total_week_intake = sum(item['total_ml'] for item in summary_data)
    avg_daily_intake = total_week_intake / 7
    days_target_met = sum(1 for item in summary_data if item['total_ml'] >= RECOMMENDED_DAILY_INTAKE)
    
    # Display summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Weekly Intake", f"{total_week_intake} ml")
    
    with col2:
        st.metric("Average Daily Intake", f"{int(avg_daily_intake)} ml")
    
    with col3:
        st.metric("Days Target Met", f"{days_target_met}/7")
    
    # Tips based on water intake
    st.subheader("Hydration Tips")
    
    if avg_daily_intake < RECOMMENDED_DAILY_INTAKE * 0.6:
        st.warning("""
        **You're not drinking enough water!** 
        - Set reminders to drink water throughout the day
        - Keep a water bottle with you at all times
        - Try drinking a glass of water before each meal
        """)
    elif avg_daily_intake < RECOMMENDED_DAILY_INTAKE:
        st.info("""
        **You're doing okay, but could drink more water!**
        - Try drinking a glass of water when you wake up
        - Flavor your water with fruits if you find plain water boring
        - Track your intake regularly to build the habit
        """)
    else:
        st.success("""
        **Great job staying hydrated!**
        - Keep up the good work
        - Remember to adjust your intake when exercising or in hot weather
        - Consistency is key to staying properly hydrated
        """) 