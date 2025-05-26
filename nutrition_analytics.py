import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import get_nutrition_data, get_performance_metrics, get_nutrition_performance_correlation, get_meal_details

def display_nutrition_analytics_page(user_id):
    """
    Display the nutrition analytics page with performance correlation
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function display_nutrition_analytics_page(user_id) that creates a Streamlit page with three tabs for nutrition analytics: "Performance Correlation," "Nutrition Trends," and "Detailed Analysis." The function should display a title with an appropriate emoji, create the tab structure, and call separate display functions for each tab while passing the user_id parameter to each function.
    """
    
    st.title("📊 Nutrition & Performance Analytics")
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["Performance Correlation", "Nutrition Trends", "Detailed Analysis"])
    
    with tab1:
        display_correlation_analysis(user_id)
    
    with tab2:
        display_nutrition_trends(user_id)
    
    with tab3:
        display_detailed_analysis(user_id)


def display_correlation_analysis(user_id):
    """
    Display correlation analysis between nutrition and workout performance
    """
    
    """
    AI Prompt:
    Write a Python function display_correlation_analysis(user_id) that creates a Streamlit data visualization showing correlations between nutrition metrics (calories, protein, carbs, water) and workout performance (distance, steps, calories burned). The function should fetch correlation data, create scatter plots with Plotly, display correlation metrics with appropriate formatting and color coding, and provide personalized insights based on the correlation strengths, handling edge cases like insufficient data with helpful messages.
    """
    
    st.header("Nutrition & Performance Correlation")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("Data period (days)", min_value=7, max_value=90, value=30, step=1)
    
    with col2:
        st.info(f"Analyzing data from the last {days} days")
    
    # Get correlated data
    try:
        correlated_data = get_nutrition_performance_correlation(user_id, days)
        
        if not correlated_data:
            st.warning("No data available for correlation analysis.")
            st.markdown("""
            ### How to Get Started with Analytics
            To see nutrition and performance insights:
            1. Log your meals using the **Meal Logger** 
            2. Record your workouts regularly
            3. Track your water intake daily
            
            Once you have at least a week of data, you'll start seeing personalized insights here!
            """)
            return
        
        # Convert to DataFrame for analysis
        df_list = []
        for date, data in correlated_data.items():
            if data['nutrition'] and data['performance']:
                combined = {
                    'date': date,
                    'total_calories': data['nutrition']['total_calories'],
                    'total_protein': data['nutrition']['total_protein'],
                    'total_carbs': data['nutrition']['total_carbs'],
                    'total_fat': data['nutrition']['total_fat'],
                    'total_water_ml': data['nutrition']['total_water_ml'],
                    'distance': data['performance']['distance'],
                    'steps': data['performance']['steps'],
                    'calories_burned': data['performance']['calories_burned']
                }
                df_list.append(combined)
        
        if not df_list:
            st.warning("Not enough matched data for correlation analysis.")
            st.markdown("""
            ### Why Am I Seeing This Message?
            You need both nutrition and workout data on the same days to see correlations.
            
            **Try This:**
            - Make sure you log your nutrition and workouts on the same days
            - Log consistently for at least a week
            - Include variety in your nutrition and workouts
            """)
            return
            
        if len(df_list) < 3:
            st.warning(f"Only {len(df_list)} days with both nutrition and workout data. More data will give better insights.")
        
        df = pd.DataFrame(df_list)
        
        # Main correlation visualization
        st.subheader("How Nutrition Affects Your Workout Performance")
        
        # Create Plotly figure with multiple traces
        fig = make_subplots(rows=2, cols=2, 
                            subplot_titles=("Calories & Performance", "Protein & Performance", 
                                            "Carbs & Performance", "Water & Performance"))
        
        # 1. Calories vs Workout Performance
        fig.add_trace(
            go.Scatter(x=df['total_calories'], y=df['calories_burned'], mode='markers', 
                       marker=dict(size=10, color='blue'), name='Calories Burned'),
            row=1, col=1
        )
        
        # 2. Protein vs Workout Performance
        fig.add_trace(
            go.Scatter(x=df['total_protein'], y=df['distance'], mode='markers', 
                       marker=dict(size=10, color='green'), name='Distance'),
            row=1, col=2
        )
        
        # 3. Carbs vs Workout Performance
        fig.add_trace(
            go.Scatter(x=df['total_carbs'], y=df['steps'], mode='markers', 
                       marker=dict(size=10, color='orange'), name='Steps'),
            row=2, col=1
        )
        
        # 4. Water vs Performance
        fig.add_trace(
            go.Scatter(x=df['total_water_ml'], y=df['calories_burned'], mode='markers', 
                       marker=dict(size=10, color='cyan'), name='Calories Burned'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(height=600, width=800, title_text="Nutrition & Performance Correlations", 
                          showlegend=False)
        
        # Update axes titles
        fig.update_xaxes(title_text="Calories Consumed", row=1, col=1)
        fig.update_yaxes(title_text="Calories Burned", row=1, col=1)
        
        fig.update_xaxes(title_text="Protein (g)", row=1, col=2)
        fig.update_yaxes(title_text="Distance (miles)", row=1, col=2)
        
        fig.update_xaxes(title_text="Carbs (g)", row=2, col=1)
        fig.update_yaxes(title_text="Steps", row=2, col=1)
        
        fig.update_xaxes(title_text="Water (ml)", row=2, col=2)
        fig.update_yaxes(title_text="Calories Burned", row=2, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display correlation insights
        st.subheader("Key Insights")
        
        # Calculate correlations
        corr_cal = df['total_calories'].corr(df['calories_burned'])
        corr_protein = df['total_protein'].corr(df['distance'])
        corr_carbs = df['total_carbs'].corr(df['steps'])
        corr_water = df['total_water_ml'].corr(df['calories_burned'])
        
        # Function to format correlation values with user-friendly display
        def format_correlation(corr_value):
            if pd.isna(corr_value):
                return "No pattern detected"
            elif abs(corr_value) < 0.2:
                return f"{corr_value:.2f} (Weak)"
            elif abs(corr_value) < 0.6:
                return f"{corr_value:.2f} (Moderate)"
            else:
                return f"{corr_value:.2f} (Strong)"
        
        # Function to determine the correlation color
        def get_correlation_delta_color(corr_value):
            if pd.isna(corr_value):
                return "off"
            elif corr_value > 0:
                return "normal"  # Green for positive correlation
            else:
                return "inverse"  # Red for negative correlation
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Protein & Distance Correlation", 
                format_correlation(corr_protein),
                delta=None if pd.isna(corr_protein) else f"{corr_protein:.2f}",
                delta_color=get_correlation_delta_color(corr_protein)
            )
            st.metric(
                "Carbs & Steps Correlation", 
                format_correlation(corr_carbs),
                delta=None if pd.isna(corr_carbs) else f"{corr_carbs:.2f}",
                delta_color=get_correlation_delta_color(corr_carbs)
            )
        
        with col2:
            st.metric(
                "Calories & Workout Performance", 
                format_correlation(corr_cal),
                delta=None if pd.isna(corr_cal) else f"{corr_cal:.2f}",
                delta_color=get_correlation_delta_color(corr_cal)
            )
            st.metric(
                "Water Intake & Performance", 
                format_correlation(corr_water),
                delta=None if pd.isna(corr_water) else f"{corr_water:.2f}",
                delta_color=get_correlation_delta_color(corr_water)
            )
        
        # Add explanation about correlations
        with st.expander("What do these correlation values mean?"):
            st.write("""
            **Correlation values range from -1 to 1:**
            - **Positive values (0 to 1)**: As one metric increases, the other also increases.
            - **Negative values (-1 to 0)**: As one metric increases, the other decreases.
            - **Values near zero**: Little to no relationship between the metrics.
            - **Values near -1 or 1**: Strong relationship between the metrics.
            
            If you see "No pattern detected," it means there's not enough variation in the data to calculate a correlation.
            Add more diverse nutrition and workout data to see patterns emerge.
            """)
        
        # Generate insights based on correlations
        st.markdown("### Personalized Recommendations")
        
        insights = []

        # Check if we have enough data to make recommendations
        if pd.isna(corr_protein) and pd.isna(corr_carbs) and pd.isna(corr_cal) and pd.isna(corr_water):
            st.info("We need more data to generate personalized recommendations. Try logging your nutrition and workout data consistently for at least a week.")
            return

        # Protein insights
        if not pd.isna(corr_protein):
            if corr_protein > 0.3:
                insights.append("✅ **Higher protein intake is associated with longer workout distances** - Keep maintaining good protein intake before workouts")
            elif corr_protein < -0.3:
                insights.append("⚠️ **Your protein intake and workout distance show an unusual pattern** - Consider timing your protein intake better relative to workouts")
            elif abs(corr_protein) < 0.2:
                insights.append("ℹ️ **Your protein intake doesn't show a strong relationship with workout distance** - Try experimenting with protein timing and sources")
        else:
            insights.append("ℹ️ **We can't determine a pattern between your protein intake and workout distance yet** - Continue logging both nutrition and workouts")
        
        # Carbs insights
        if not pd.isna(corr_carbs):
            if corr_carbs > 0.3:
                insights.append("✅ **Carbohydrate intake is positively correlated with your step count** - Carbs are providing good energy for your activities")
            elif corr_carbs < 0:
                insights.append("⚠️ **Your carb intake doesn't seem to boost your step count** - Consider adjusting when you consume carbs for better energy")
            elif abs(corr_carbs) < 0.2:
                insights.append("ℹ️ **Carbs are showing minimal impact on your step count** - Try complex carbs 2-3 hours before activity")
        
        # Water insights
        if not pd.isna(corr_water):
            if corr_water > 0.3:
                insights.append("✅ **Higher water intake correlates with more calories burned** - Staying hydrated is helping your workout performance")
            elif corr_water < 0:
                insights.append("⚠️ **Unusual pattern between water intake and calories burned** - Are you logging all your water intake?")
            else:
                insights.append("ℹ️ **Increase your water intake to potentially improve workout performance** - Aim for at least 2000ml daily")
        else:
            insights.append("💧 **Make sure to log your water intake** - Hydration is critical for performance and recovery")
        
        # Calories insights
        if not pd.isna(corr_cal):
            if corr_cal > 0.5:
                insights.append("✅ **Your calorie intake is well-balanced with your exercise level** - This balanced approach supports sustainable fitness")
            elif corr_cal < 0:
                insights.append("⚠️ **Your calorie intake appears inversely related to workout performance** - Check your meal timing relative to workouts")
        
        # General recommendations if we have very few insights
        if len(insights) < 2:
            insights.append("📊 **Add more varied nutrition and workout data to get better insights** - Try to log consistently for at least a week")
            insights.append("🔄 **Experiment with different nutrition patterns** - Record how you feel during workouts to identify what works best for you")
        
        # Display insights with better formatting
        for i, insight in enumerate(insights):
            st.markdown(f"{insight}")
            
            # Add separator except after the last insight
            if i < len(insights) - 1:
                st.markdown("---")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def display_nutrition_trends(user_id):
    """
    Display trends in nutrition data over time
    """
    
    """
    AI Prompt:
    Write a Python function display_nutrition_trends(user_id) that visualizes a user's nutrition data trends over time using Streamlit and Plotly. The function should create time-series charts for macronutrient distribution (stacked area chart), daily calorie intake (line chart), water intake (line chart), and macronutrient ratio (pie chart), with dynamic analysis of the user's macronutrient balance providing color-coded success/warning messages based on nutritional guidelines.
    """
    
    st.header("Nutrition Trends")
    
    # Date range selector
    days = st.slider("Trend period (days)", min_value=7, max_value=90, value=30, step=1, key="trend_days")
    
    # Get nutrition data
    nutrition_data = get_nutrition_data(user_id, days)
    
    if not nutrition_data:
        st.warning("No nutrition data available for the selected period.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(nutrition_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create visualization for macronutrient distribution over time
    st.subheader("Macronutrient Distribution Over Time")
    
    # Create stacked area chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['total_protein'],
        mode='lines',
        stackgroup='one',
        name='Protein',
        line=dict(width=0.5, color='rgb(0, 128, 0)'),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['total_carbs'],
        mode='lines',
        stackgroup='one',
        name='Carbs',
        line=dict(width=0.5, color='rgb(255, 165, 0)'),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['total_fat'],
        mode='lines',
        stackgroup='one',
        name='Fat',
        line=dict(width=0.5, color='rgb(255, 0, 0)'),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title='Daily Macronutrients',
        xaxis_title='Date',
        yaxis_title='Grams',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display calorie and water intake trends
    col1, col2 = st.columns(2)
    
    with col1:
        # Calorie intake trend
        fig_cal = px.line(df, x='date', y='total_calories', title='Daily Calorie Intake')
        fig_cal.update_traces(line_color='#1E88E5')
        
        # Add target line
        fig_cal.add_hline(y=2000, line_dash="dash", line_color="red",
                      annotation_text="Target Calories", 
                      annotation_position="bottom right")
        
        st.plotly_chart(fig_cal, use_container_width=True)
        
    with col2:
        # Water intake trend
        fig_water = px.line(df, x='date', y='total_water_ml', title='Daily Water Intake')
        fig_water.update_traces(line_color='#00BCD4')
        
        # Add target line
        fig_water.add_hline(y=2000, line_dash="dash", line_color="blue",
                        annotation_text="Target Water Intake", 
                        annotation_position="bottom right")
        
        st.plotly_chart(fig_water, use_container_width=True)
    
    # Calculate average macronutrient ratios
    avg_protein = df['total_protein'].mean()
    avg_carbs = df['total_carbs'].mean()
    avg_fat = df['total_fat'].mean()
    total_macros = avg_protein + avg_carbs + avg_fat
    
    # Safety check to avoid division by zero
    if total_macros > 0:
        protein_pct = (avg_protein / total_macros) * 100
        carbs_pct = (avg_carbs / total_macros) * 100
        fat_pct = (avg_fat / total_macros) * 100
        
        # Display macronutrient distribution pie chart
        st.subheader("Average Macronutrient Distribution")
        
        fig_pie = px.pie(
            values=[protein_pct, carbs_pct, fat_pct],
            names=['Protein', 'Carbs', 'Fat'],
            color_discrete_sequence=['green', 'orange', 'red'],
            title='Macronutrient Ratio'
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Add some insights about macronutrient distribution
        st.subheader("Macronutrient Analysis")
        
        if protein_pct < 15:
            st.warning("Your protein intake is on the low side. Consider increasing protein for better muscle recovery.")
        elif protein_pct > 35:
            st.info("Your protein intake is quite high. While good for building muscle, ensure you're getting enough other nutrients.")
        else:
            st.success("Your protein intake is in a healthy range.")
            
        if carbs_pct < 30:
            st.info("Your carbohydrate intake is relatively low. This might work well if you're focusing on fat burning.")
        elif carbs_pct > 60:
            st.warning("Your carbohydrate intake is quite high. Consider balancing with more protein and healthy fats.")
        else:
            st.success("Your carbohydrate intake is in a balanced range.")
            
        if fat_pct < 15:
            st.warning("Your fat intake is low. Healthy fats are essential for hormone production and vitamin absorption.")
        elif fat_pct > 40:
            st.info("Your fat intake is on the higher side. Consider the types of fats you're consuming - focus on unsaturated sources.")
        else:
            st.success("Your fat intake is in a healthy range.")


def display_detailed_analysis(user_id):
    """
    Display detailed nutrition and meal analysis
    """
    
    """
    AI Prompt:
    Write a Python function display_detailed_analysis(user_id) that creates an in-depth nutritional analysis dashboard in Streamlit, analyzing the user's meal data to show calorie distribution by meal type, most frequently consumed foods, and meal timing patterns. The function should combine nutrition and workout timing data to provide personalized recommendations on optimal meal timing before workouts, while handling cases with insufficient data gracefully and providing an expandable view of the raw nutrition data.
    """
    
    st.header("Detailed Nutrition Analysis")
    
    # Date range selector
    days = st.slider("Analysis period (days)", min_value=7, max_value=90, value=14, step=1, key="detailed_days")
    
    # Get meal details
    meal_data = get_meal_details(user_id, days)
    
    if not meal_data:
        st.warning("No meal data available for the selected period.")
        return
    
    # Convert to DataFrame
    df_meals = pd.DataFrame(meal_data)
    df_meals['meal_time'] = pd.to_datetime(df_meals['meal_time'])
    df_meals['date'] = df_meals['meal_time'].dt.date
    
    # Group by meal type
    st.subheader("Calories by Meal Type")
    
    meal_type_calories = df_meals.groupby('meal_type')['total_calories'].sum().reset_index()
    
    fig_meal_types = px.bar(
        meal_type_calories, 
        x='meal_type', 
        y='total_calories',
        color='meal_type',
        title='Calorie Distribution by Meal Type'
    )
    
    st.plotly_chart(fig_meal_types, use_container_width=True)
    
    # Most common foods
    st.subheader("Most Common Foods")
    
    food_counts = df_meals['food_name'].value_counts().reset_index()
    food_counts.columns = ['Food', 'Count']
    food_counts = food_counts.head(10)  # Top 10 foods
    
    fig_foods = px.bar(
        food_counts, 
        x='Count', 
        y='Food',
        orientation='h',
        title='Your Most Frequently Consumed Foods',
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    st.plotly_chart(fig_foods, use_container_width=True)
    
    # Meal timing analysis
    st.subheader("Meal Timing Analysis")
    
    # Add hour of day
    df_meals['hour'] = df_meals['meal_time'].dt.hour
    
    # Group by hour and meal type
    hour_meal_calories = df_meals.groupby(['hour', 'meal_type'])['total_calories'].sum().reset_index()
    
    fig_timing = px.line(
        hour_meal_calories,
        x='hour',
        y='total_calories',
        color='meal_type',
        title='Calorie Intake by Time of Day',
        labels={'hour': 'Hour of Day', 'total_calories': 'Calories'}
    )
    
    # Format x-axis to show hours
    fig_timing.update_xaxes(tickvals=list(range(0, 24)), ticktext=[f"{h}:00" for h in range(0, 24)])
    
    st.plotly_chart(fig_timing, use_container_width=True)
    
    # Insights for workout optimization
    st.subheader("Nutrition & Workout Timing Insights")
    
    # Get performance data
    performance_data = get_performance_metrics(user_id, days)
    
    if performance_data:
        # Create DataFrame for workouts
        df_workouts = pd.DataFrame(performance_data)
        df_workouts['start_time'] = pd.to_datetime(df_workouts['start_timestamp'])
        df_workouts['date'] = df_workouts['start_time'].dt.date
        df_workouts['hour'] = df_workouts['start_time'].dt.hour
        
        # Generate pre-workout and post-workout nutrition insights
        workout_dates = set(df_workouts['date'])
        meals_on_workout_days = df_meals[df_meals['date'].isin(workout_dates)]
        
        # Analyze pre-workout nutrition
        workout_meal_insights = []
        
        for idx, workout in df_workouts.iterrows():
            workout_date = workout['date']
            workout_hour = workout['hour']
            
            # Get meals before workout (same day)
            pre_workout_meals = meals_on_workout_days[
                (meals_on_workout_days['date'] == workout_date) & 
                (meals_on_workout_days['meal_time'].dt.hour < workout_hour)
            ]
            
            if not pre_workout_meals.empty:
                # Calculate pre-workout nutrition
                hours_before = [(workout_hour - meal_hour) for meal_hour in pre_workout_meals['meal_time'].dt.hour]
                closest_meal_idx = hours_before.index(min(hours_before))
                closest_meal = pre_workout_meals.iloc[closest_meal_idx]
                
                workout_meal_insights.append({
                    'workout_date': workout_date,
                    'workout_time': workout['start_time'],
                    'calories_burned': workout['calories_burned'],
                    'distance': workout['distance'],
                    'pre_workout_meal_type': closest_meal['meal_type'],
                    'pre_workout_calories': closest_meal['total_calories'],
                    'pre_workout_carbs': closest_meal['total_carbs_grams'],
                    'pre_workout_protein': closest_meal['total_protein_grams'],
                    'hours_before_workout': min(hours_before)
                })
        
        if workout_meal_insights:
            df_insights = pd.DataFrame(workout_meal_insights)
            
            # Analyze correlation between pre-workout nutrition and performance
            st.markdown("### Pre-Workout Nutrition Impact")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Correlation: Pre-workout carbs vs. Distance
                fig_carb_dist = px.scatter(
                    df_insights, 
                    x='pre_workout_carbs', 
                    y='distance',
                    color='hours_before_workout',
                    title='Pre-Workout Carbs vs. Workout Distance',
                    labels={'pre_workout_carbs': 'Carbs before workout (g)', 'distance': 'Distance (miles)'}
                )
                st.plotly_chart(fig_carb_dist, use_container_width=True)
            
            with col2:
                # Correlation: Hours before workout vs. Calories burned
                fig_timing_perf = px.scatter(
                    df_insights, 
                    x='hours_before_workout', 
                    y='calories_burned',
                    color='pre_workout_calories',
                    title='Meal Timing vs. Calories Burned',
                    labels={'hours_before_workout': 'Hours before workout', 'calories_burned': 'Calories Burned'}
                )
                st.plotly_chart(fig_timing_perf, use_container_width=True)
            
            # Generate optimization recommendations
            st.markdown("### Optimization Recommendations")
            
            avg_best_hours = df_insights.sort_values('calories_burned', ascending=False).head(3)['hours_before_workout'].mean()
            best_pre_workout_meal = df_insights.sort_values('calories_burned', ascending=False).iloc[0]['pre_workout_meal_type']
            
            st.success(f"**Optimal meal timing:** Eat approximately {avg_best_hours:.1f} hours before your workout for best results")
            st.success(f"**Best pre-workout meal type:** {best_pre_workout_meal}")
            
            # Carb recommendation based on correlation
            carb_corr = df_insights['pre_workout_carbs'].corr(df_insights['distance'])
            if carb_corr > 0.3:
                st.info("Higher carbohydrate intake before workouts is associated with better performance in your case")
            elif carb_corr < -0.3:
                st.info("Your data suggests that too many carbs before a workout might be reducing your performance")
        else:
            st.info("Not enough data to analyze pre-workout nutrition patterns. Log more meals and workouts to get insights.")
    else:
        st.info("No workout data available to correlate with nutrition. Add workout data to see insights.")
        
    # Display raw data in expandable section
    with st.expander("View Raw Nutrition Data"):
        st.dataframe(df_meals) 