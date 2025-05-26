import streamlit as st
import matplotlib.pyplot as plt
from data_fetcher import add_meal, get_user_nutrition_goals, get_all_food_items, get_user_meals, add_food_to_meal

def show(user_id):
    st.title("Add Meal")

    # Get current goals
    current_goals = get_user_nutrition_goals(user_id)
    if not current_goals:
        st.warning("Please set your nutrition goals first in the 'Set Goals' page.")
        return

    # Get current meals
    current_meals = get_user_meals(user_id)
    
    # Calculate current macronutrients
    total_fats = 0
    total_protein = 0
    total_carbs = 0
    for meal in current_meals:
        total_fats += meal["fat_grams"]
        total_protein += meal["protein_grams"]
        total_carbs += meal["carbs_grams"]
    
    # Macronutrient chart
    st.subheader("Current Macronutrients Summary:")
    fig, ax = plt.subplots(figsize=(3, 3))

    labels = ["Fats", "Carbs", "Protein"]
    values = [total_fats, total_carbs, total_protein]
    colors = ["#41b8d5", "#6ce5e8", "#2f5f98"]  # match prototype

    ax.pie(values, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Meal type selection
    meal_type = st.selectbox("Meal type:", ["Select", "Breakfast", "Lunch", "Dinner"])

    # Get all food items
    all_food_items = get_all_food_items()
    
    # Create a map of display names to food IDs for selection
    food_display_options = [item["display_name"] for item in all_food_items]
    food_id_map = {item["display_name"]: item["food_id"] for item in all_food_items}
    
    # Food item selection
    selected_food_displays = st.multiselect("Select Foods:", food_display_options)
    
    # Optional meal name
    meal_name = st.text_input("Meal Name (optional):", placeholder="e.g., Post-workout meal")

    # Save button
    if st.button("Save"):
        if meal_type == "Select" or not selected_food_displays:
            st.warning("Please select a meal type and at least one food item.")
        else:
            # Create the meal
            meal_id = add_meal(user_id, meal_type.lower(), meal_name if meal_name else None)
            
            if meal_id:
                # Add each selected food to the meal
                success = True
                for food_display in selected_food_displays:
                    food_id = food_id_map[food_display]
                    # Default quantity 1.0 - could add quantity controls for each food item
                    result = add_food_to_meal(meal_id, food_id, 1.0)
                    if not result:
                        success = False
                
                if success:
                    st.success("Meal added successfully!")
                else:
                    st.warning("Meal created but some food items could not be added.")
                
                st.rerun()
            else:
                st.error("Failed to create meal. Please try again.")

