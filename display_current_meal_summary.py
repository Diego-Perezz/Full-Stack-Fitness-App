"""
AI Prompt:
Write a Python function display_current_meal_summary(meal_id) that displays a Streamlit summary of a meal being logged, showing the total nutritional content (calories, protein, carbs, fat) and listing each food item with its nutritional breakdown. The function should fetch meal details using a cached function, handle empty meals with an informative message, and gracefully catch any exceptions without exposing technical details to the user.
"""

import streamlit as st
from meal_logger import get_cached_meal_details

def display_current_meal_summary(meal_id):
    """
    Display summary of the current meal being logged
    
    Args:
        meal_id (str): ID of the current meal
    """
    try:
        # Use cached version to get meal details
        all_meals = get_cached_meal_details('user1', days=1)  # Use a default user_id and small time window
        foods = [food for food in all_meals if food.get('meal_id') == meal_id]
        
        if foods:
            st.subheader("Current Meal Summary")
            
            # Calculate totals
            total_calories = sum(food.get('total_calories', 0) for food in foods)
            total_protein = sum(food.get('total_protein_grams', 0) for food in foods)
            total_carbs = sum(food.get('total_carbs_grams', 0) for food in foods)
            total_fat = sum(food.get('total_fat_grams', 0) for food in foods)
            
            # Display totals
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Calories", f"{total_calories:.0f}")
            col2.metric("Protein", f"{total_protein:.1f}g")
            col3.metric("Carbs", f"{total_carbs:.1f}g")
            col4.metric("Fat", f"{total_fat:.1f}g")
            
            # Display foods in the meal
            st.write("Foods in this meal:")
            
            for food in foods:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{food.get('food_name', 'Unknown')}** ({food.get('quantity', 0)} servings)")
                    st.caption(f"{food.get('total_calories', 0):.0f} cal, P: {food.get('total_protein_grams', 0):.1f}g, C: {food.get('total_carbs_grams', 0):.1f}g, F: {food.get('total_fat_grams', 0):.1f}g")
                
                # TODO: Add a remove button if needed
                
                st.markdown("---")
        else:
            # Display a message without revealing technical details
            st.info("No foods added to this meal yet. Search for foods to add them.")
    except Exception as e:
        # Log the error but don't show it to the user
        print(f"Error displaying meal summary: {str(e)}")
        st.info("Unable to display meal summary. Please try again.") 