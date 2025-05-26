import streamlit as st
import pandas as pd
import datetime
from data_fetcher import (
    add_meal, add_food_to_meal, search_food_items, 
    add_custom_food_item, get_meal_details
)

# Add caching for meal data
@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes, hide spinner
def get_cached_meal_details(user_id, days=30):
    """Cached version of get_meal_details to improve performance"""
    
    """
    AI Prompt:
    Write a Python function get_cached_meal_details(user_id, days=30) that implements a cached version of the get_meal_details function using Streamlit's cache_data decorator with a 5-minute time-to-live and hidden spinner. The function should accept a user ID and optional number of days parameter (defaulting to 30), and return cached meal details to improve performance when retrieving the same data multiple times.
    """
    
    return get_meal_details(user_id, days)

def display_meal_logger_page(user_id):
    """
    Display the meal logging page
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function display_meal_logger_page(user_id) that creates a Streamlit page for meal logging with three tabs: "Log Meal", "Add Custom Food", and "Meal History". The function should call separate display functions for each tab, passing the user_id parameter to functions that require it, and create a clear visual organization with appropriate titles and tab labels.
    """
    
    st.title("🍽️ Meal Logger")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Log Meal", "Add Custom Food", "Meal History"])
    
    with tab1:
        display_meal_logger(user_id)
    
    with tab2:
        display_custom_food_form()
    
    with tab3:
        # Since we're in this tab, we'll load the history
        display_meal_history(user_id)

def display_meal_logger(user_id):
    """
    Display interface for logging meals
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function display_meal_logger(user_id) that creates a Streamlit form for logging meals with fields for meal type, name, date, and time, then handles form submission by creating a meal record and showing a food search interface. The function should manage session state to track the current meal being created, handle success and error cases appropriately, and rerun the page when needed to update the UI after state changes.
    """
    
    st.header("Log a Meal")
    
    # Set up the meal logging form
    with st.form("meal_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            meal_type = st.selectbox(
                "Meal Type",
                options=["breakfast", "lunch", "dinner", "snack"],
                key="meal_type"
            )
            
            meal_name = st.text_input(
                "Meal Name (optional)",
                placeholder="e.g., Post-workout shake",
                key="meal_name"
            )
        
        with col2:
            meal_date = st.date_input(
                "Date",
                value=datetime.datetime.now().date(),
                key="meal_date"
            )
            
            meal_time = st.time_input(
                "Time",
                value=datetime.datetime.now().time(),
                key="meal_time"
            )
        
        # Combine date and time
        meal_datetime = datetime.datetime.combine(meal_date, meal_time)
        
        # Submit button
        submit_meal = st.form_submit_button("Create Meal")
    
    # Handle meal creation
    if submit_meal:
        meal_id = add_meal(
            user_id=user_id,
            meal_type=meal_type,
            meal_name=meal_name if meal_name else None,
            meal_time=meal_datetime
        )
        
        if meal_id:
            st.success(f"Meal created successfully!")
            # Store meal_id in session state for adding foods
            st.session_state.current_meal_id = meal_id
            st.session_state.show_food_search = True
            # Force a rerun to show the food search section
            st.rerun()
        else:
            st.error("Failed to create meal. Please try again.")
    
    # Show food search after meal is created
    if 'show_food_search' in st.session_state and st.session_state.show_food_search:
        display_food_search()

def display_food_search():
    """
    Display interface for searching and adding foods to a meal
    """
    
    """
    AI Prompt:
    Write a Python function display_food_search() that creates a Streamlit interface for searching food items, displaying search results in a formatted list with nutritional information, and allowing users to select quantities and add items to the current meal. The function should handle search queries, display appropriate messages when no results are found, show the current meal summary using a separate function, and include a button to finish the meal logging process.
    """
    
    st.subheader("Add Foods to Your Meal")
    
    # Search interface
    search_query = st.text_input(
        "Search for food",
        placeholder="Enter food name or brand",
        key="food_search"
    )
    
    # Display search results if user has entered a query
    if search_query:
        food_items = search_food_items(search_query)
        
        if not food_items:
            st.info("No foods found matching your search. Try a different term or add a custom food.")
        else:
            st.write(f"Found {len(food_items)} items:")
            
            # Display food items in a table for selection
            df_foods = pd.DataFrame(food_items)
            df_foods.rename(columns={
                'food_name': 'Food',
                'brand_name': 'Brand', 
                'serving_size_grams': 'Serving Size (g)',
                'calories': 'Calories',
                'protein_grams': 'Protein (g)',
                'carbs_grams': 'Carbs (g)',
                'fat_grams': 'Fat (g)'
            }, inplace=True)
            
            # Display the table with select buttons
            for index, row in df_foods.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{row['Food']}** - {row['Brand']}")
                    st.caption(f"{row['Calories']} cal, P: {row['Protein (g)']}g, C: {row['Carbs (g)']}g, F: {row['Fat (g)']}g")
                
                with col2:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=0.1,
                        max_value=10.0,
                        value=1.0,
                        step=0.1,
                        key=f"quantity_{index}"
                    )
                
                with col3:
                    food_id = food_items[index]['food_id']
                    if st.button("Add", key=f"add_{index}"):
                        if 'current_meal_id' in st.session_state:
                            success = add_food_to_meal(
                                meal_id=st.session_state.current_meal_id,
                                food_id=food_id,
                                quantity=quantity
                            )
                            
                            if success:
                                st.success(f"Added {row['Food']} to meal.")
                                # Reload the page to update the meal summary
                                st.rerun()
                            else:
                                st.error("Failed to add food to meal.")
                
                st.markdown("---")
    
    # Display current meal summary if a meal is in progress
    if 'current_meal_id' in st.session_state:
        display_current_meal_summary(st.session_state.current_meal_id)
    
    # Finish meal button
    if st.button("Finish Logging Meal"):
        if 'current_meal_id' in st.session_state:
            # Clear the session state to start fresh
            st.session_state.pop('current_meal_id', None)
            st.session_state.pop('show_food_search', None)
            st.success("Meal logged successfully!")
            st.rerun()

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

def display_custom_food_form():
    """
    Display form for adding custom food items
    """
    
    """
    AI Prompt:
    Write a Python function display_custom_food_form() that creates a Streamlit form for adding custom food items with fields for name, brand, serving size, macronutrients (calories, protein, carbs, fat), and optional micronutrients. The function should validate form submissions by checking required fields, verify that macronutrient values approximately match the calorie count, and display appropriate success or error messages after attempting to add the custom food to the database.
    """
    
    st.header("Add Custom Food")
    st.write("Create a custom food item to add to your meals.")
    
    with st.form("custom_food_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            food_name = st.text_input(
                "Food Name",
                placeholder="e.g., Homemade Granola"
            )
            
            brand_name = st.text_input(
                "Brand (optional)",
                placeholder="e.g., Homemade",
                value="Homemade"
            )
            
            serving_size = st.number_input(
                "Serving Size (grams)",
                min_value=1.0,
                max_value=1000.0,
                value=100.0,
                step=1.0
            )
        
        with col2:
            calories = st.number_input(
                "Calories per serving",
                min_value=0.0,
                max_value=2000.0,
                value=0.0,
                step=1.0
            )
            
            protein = st.number_input(
                "Protein (grams)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )
            
            carbs = st.number_input(
                "Carbohydrates (grams)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )
            
            fat = st.number_input(
                "Fat (grams)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )
        
        # Additional nutrients (in expander)
        with st.expander("Additional Nutrients (optional)"):
            fiber = st.number_input(
                "Fiber (grams)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )
            
            sugar = st.number_input(
                "Sugar (grams)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1
            )
            
            sodium = st.number_input(
                "Sodium (milligrams)",
                min_value=0.0,
                max_value=5000.0,
                value=0.0,
                step=1.0
            )
        
        # Submit button
        submit_food = st.form_submit_button("Add Custom Food")
    
    # Handle food creation
    if submit_food:
        if not food_name:
            st.error("Food name is required.")
            return
        
        # Validate macros add up approximately to calories
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        if calories > 0 and abs(calculated_calories - calories) > 20:
            st.warning(f"The calories ({calories}) don't match the calculated value from macros ({calculated_calories:.1f}). Please check your numbers.")
        
        food_id = add_custom_food_item(
            food_name=food_name,
            brand_name=brand_name,
            serving_size_grams=serving_size,
            calories=calories,
            protein_grams=protein,
            carbs_grams=carbs,
            fat_grams=fat,
            fiber_grams=fiber,
            sugar_grams=sugar,
            sodium_mg=sodium
        )
        
        if food_id:
            st.success(f"Custom food '{food_name}' added successfully! You can now use it in your meals.")
        else:
            st.error("Failed to add custom food. Please try again.")

def display_meal_history(user_id):
    """
    Display meal history for the user with pagination for better performance
    
    Args:
        user_id (str): The ID of the current user
    """
    
    """
    AI Prompt:
    Write a Python function display_meal_history(user_id) that shows a paginated history of user meals with a date range slider, nutritional summaries, and expandable details for each meal. The function should process meal data to group foods by meal ID, calculate total nutritional values for each meal, implement pagination controls with proper state management, and handle exceptions gracefully without exposing technical details to the user.
    """
    
    try:
        st.header("Meal History")
        
        # Date selector for history
        days = st.slider("Show meals from the last", min_value=1, max_value=30, value=7, step=1, key="history_days")
        
        # Use cached version of get_meal_details
        meal_data = get_cached_meal_details(user_id=user_id, days=days)
        
        if not meal_data:
            st.info("No meal data available for the selected period.")
            return
        
        # Group by meal_id to consolidate foods in the same meal - do this processing once
        meals_by_id = {}
        for food in meal_data:
            meal_id = food.get('meal_id')
            meal_time = food.get('meal_time')
            meal_type = food.get('meal_type')
            meal_name = food.get('meal_name')
            
            if meal_id not in meals_by_id:
                meals_by_id[meal_id] = {
                    'meal_id': meal_id,
                    'meal_time': meal_time,
                    'meal_type': meal_type,
                    'meal_name': meal_name,
                    'foods': [],
                    'total_calories': 0,
                    'total_protein': 0,
                    'total_carbs': 0,
                    'total_fat': 0
                }
            
            meals_by_id[meal_id]['foods'].append(food)
            meals_by_id[meal_id]['total_calories'] += food.get('total_calories', 0)
            meals_by_id[meal_id]['total_protein'] += food.get('total_protein_grams', 0)
            meals_by_id[meal_id]['total_carbs'] += food.get('total_carbs_grams', 0)
            meals_by_id[meal_id]['total_fat'] += food.get('total_fat_grams', 0)
        
        # Convert to list and sort by meal time (most recent first)
        meals = list(meals_by_id.values())
        meals.sort(key=lambda x: x['meal_time'], reverse=True)
        
        # Implement pagination
        items_per_page = 5
        if 'meal_history_page' not in st.session_state:
            st.session_state.meal_history_page = 0
        
        # Calculate total pages
        total_pages = len(meals) // items_per_page + (1 if len(meals) % items_per_page > 0 else 0)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("← Previous", disabled=(st.session_state.meal_history_page <= 0)):
                st.session_state.meal_history_page -= 1
                st.rerun()
        
        with col2:
            st.write(f"Page {st.session_state.meal_history_page + 1} of {max(1, total_pages)}")
        
        with col3:
            if st.button("Next →", disabled=(st.session_state.meal_history_page >= total_pages - 1)):
                st.session_state.meal_history_page += 1
                st.rerun()
        
        # Get the current page of meals
        start_idx = st.session_state.meal_history_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(meals))
        current_page_meals = meals[start_idx:end_idx]
        
        # Display meals for the current page
        for meal in current_page_meals:
            try:
                # Format the date and time
                meal_datetime = datetime.datetime.fromisoformat(meal['meal_time'])
                date_str = meal_datetime.strftime("%A, %B %d")
                time_str = meal_datetime.strftime("%I:%M %p")
                
                # Create expandable section for each meal
                meal_title = f"{date_str} at {time_str} - {meal['meal_type'].capitalize()}"
                if meal['meal_name']:
                    meal_title += f" ({meal['meal_name']})"
                
                with st.expander(meal_title):
                    # Display meal summary
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Calories", f"{meal['total_calories']:.0f}")
                    col2.metric("Protein", f"{meal['total_protein']:.1f}g")
                    col3.metric("Carbs", f"{meal['total_carbs']:.1f}g")
                    col4.metric("Fat", f"{meal['total_fat']:.1f}g")
                    
                    # Display foods in the meal
                    st.write("Foods in this meal:")
                    
                    for food in meal['foods']:
                        st.write(f"**{food.get('food_name', 'Unknown')}** ({food.get('quantity', 0)} servings)")
                        st.caption(f"{food.get('total_calories', 0):.0f} cal, P: {food.get('total_protein_grams', 0):.1f}g, C: {food.get('total_carbs_grams', 0):.1f}g, F: {food.get('total_fat_grams', 0):.1f}g")
            except Exception as e:
                # Log error but don't show technical details to user
                print(f"Error displaying meal: {str(e)}")
                st.info("Unable to display this meal.")
    
    except Exception as e:
        # Log the error but don't show technical details to the user
        print(f"Error displaying meal history: {str(e)}")
        st.info("Unable to load meal history. Please try again.") 