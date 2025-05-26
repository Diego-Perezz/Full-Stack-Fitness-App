import streamlit as st
import matplotlib.pyplot as plt
from data_fetcher import get_user_nutrition_goals, get_user_meals

def show(user_id):
    """
    AI Prompt:
    Write a Python function named show that creates a nutrition overview page in Streamlit for a given user ID. Display a centered title, fetch the user's nutrition goals and meals to display a donut chart of calories consumed versus goal, and include buttons for adding meals and setting goals. Add a water intake tracker with a progress bar and buttons to increment or decrement the number of cups consumed.
    """
    
    st.markdown("<h1 style='text-align: center;'>Nutrition Overview</h1>", unsafe_allow_html=True)

    # Get current goals
    current_goals = get_user_nutrition_goals(user_id)
    if not current_goals:
        st.warning("Please set your nutrition goals first in the 'Set Goals' page.")
        return

    # Get current meals
    current_meals = get_user_meals(user_id)

    # Calculate total calories consumed
    total_calories_consumed = 0
    for meal in current_meals:
        total_calories_consumed += meal["calories"]

    # Left-aligned subtitle
    st.markdown("#### Calories consumed:")

    # Centered smaller donut chart
    consumed, goal = total_calories_consumed, current_goals["calorie_target"]
    fig, ax = plt.subplots(figsize=(1.7, 1.7))  # reduced from (3, 3)
    ax.pie([consumed, goal - consumed],
           colors=['#41b8d5', '#6ce5e8'],
           startangle=90, counterclock=False,
           wedgeprops=dict(width=0.3))
    ax.text(0, 0, f"{consumed}/{goal} kcal", ha='center', va='center', fontsize=5)
    ax.axis('equal')
    st.pyplot(fig)

    # Wide centered buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ Add Meal", use_container_width=True):
            st.query_params["page"] = "add_meal"  # Correct way to set query parameter
            st.rerun()
        if st.button("⚙️ Set Goals", use_container_width=True):
            st.query_params["page"] = "set_goals"  # Correct way to set query parameter
            st.rerun()


    # Water intake tracker
    st.markdown("---")
    st.subheader("Water intake tracker:")
    st.subheader("")

    if "cups" not in st.session_state:
        st.session_state.cups = 4

    # Centered layout using invisible side columns
    side1, main, side2 = st.columns([1, 5, 1])

    with main:
        c1, c2, c3 = st.columns([1, 7, 1])

        with c1:
            if st.button("➖", key="decrease") and st.session_state.cups > 0:
                st.session_state.cups -= 1
                st.rerun()

        with c2:
            progress_percent = int((st.session_state.cups / 8) * 100)

            st.markdown(f"""
                <div style="width: 100%; background-color: #6ce5e8; border-radius: 10px; height: 20px; margin-bottom: 6px;">
                    <div style="width: {progress_percent}%; background-color: #41b8d5; height: 100%; border-radius: 10px;"></div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(
                f"<p style='text-align: center; font-size: 16px;'>{st.session_state.cups}/8 cups</p>",
                unsafe_allow_html=True
            )

        with c3:
            if st.button("➕", key="increase") and st.session_state.cups < 8:
                st.session_state.cups += 1
                st.rerun()
