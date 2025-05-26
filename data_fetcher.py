#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import sys
import json
from datetime import datetime, timedelta
import functools
import os
import random  # Reintroduce the random import

# Import BigQuery if it's not already imported
try:
    from google.cloud import bigquery
except ImportError:
    print("BigQuery library not available. Some features will be unavailable.")

# Import Vertex AI if it's not already imported
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
except ImportError:
    print("Vertex AI library not available. AI features will be unavailable.")

# Add a memoized BigQuery client to avoid creating new connections each time
@functools.lru_cache(maxsize=1)
def get_bigquery_client():
    """
    Returns a cached instance of the BigQuery client to reduce connection overhead
    
    AI Prompt:
    Write a Python function get_bigquery_client() that returns a cached BigQuery client instance using functools.lru_cache to avoid creating multiple connections. This function should return a BigQuery client configured with the project "bamboo-creek-450920-h2" or handle exceptions gracefully.
    
    Returns:
        google.cloud.bigquery.client.Client: A BigQuery client instance
    """
    try:
        return bigquery.Client(project="bamboo-creek-450920-h2")
    except Exception as e:
        print(f"Error initializing BigQuery client: {str(e)}")
        return None

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Lebron James',
        'username': 'LeBRONJames23',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Adam sandler',
        'username': 'adam123',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://hips.hearstapps.com/hmg-prod/images/adam-sandler-gettyimages-481511486.jpg?crop=1xw:1.0xh;center,top&resize=640:*',
        'friends': ['user1', 'user3'],
    },
}

def get_user_sensor_data(user_id, workout_id):
    """
    AI Prompt:
    Write a Python function get_user_sensor_data(user_id, workout_id) 
    that fetches sensor data for a given user and workout from a BigQuery 
    table named bamboo-creek-450920-h2.ISE.SensorData
    
    
    Fetches sensor data for a specific user and workout from BigQuery.
    
    Returns a list of dictionaries with keys: sensor_type, timestamp, data, units.
    """
    # Explicitly set the project ID
    client = bigquery.Client(project="bamboo-creek-450920-h2")

    query = """
        SELECT 
            sd.SensorId AS sensor_type,
            sd.Timestamp AS timestamp,
            sd.SensorValue AS data,
            CASE 
                WHEN sd.SensorId = 'sensor1' THEN 'bpm'
                WHEN sd.SensorId = 'sensor2' THEN 'steps'
                WHEN sd.SensorId = 'sensor3' THEN '°C'
                ELSE 'unknown'
            END AS units
        FROM `bamboo-creek-450920-h2.ISE.SensorData` sd
        JOIN `bamboo-creek-450920-h2.ISE.Workouts` wd
        ON sd.WorkoutID = wd.WorkoutId
        WHERE wd.UserId = @user_id AND wd.WorkoutId = @workout_id
        ORDER BY timestamp
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id),
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    sensor_data = []
    for row in results:
        sensor_data.append({
            "sensor_type": row.sensor_type,
            "timestamp": row.timestamp.isoformat(),
            "data": row.data,
            "units": row.units
        })

    return sensor_data


def get_user_workouts(user_id):
    """Fetches a list of workouts for a given user from BigQuery.
    AI Prompt:
    
    Write an AI prompt that would generate the Python function 
    get_user_workouts(user_id) which retrieves workout data (WorkoutId, 
    StartTimestamp, EndTimestamp, StartLocationLat, StartLocationLong, 
    EndLocationLat, EndLocationLong, TotalDistance, TotalSteps, CaloriesBurned) 
    for a specific user_id from the BigQuery table
    """
    
    # Initialize the BigQuery client
    client = bigquery.Client(project="bamboo-creek-450920-h2")

    # Define the SQL query to fetch workout data for the given user
    query = """
        SELECT 
            WorkoutId,
            StartTimestamp,
            EndTimestamp,
            StartLocationLat,
            StartLocationLong,
            EndLocationLat,
            EndLocationLong,
            TotalDistance,
            TotalSteps,
            CaloriesBurned
        FROM `bamboo-creek-450920-h2.ISE.Workouts`
        WHERE UserId = @user_id
    """
    
    # Create query parameters correctly
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)  # Ensure user_id is a string
        ]
    )
    
    try:
        # Run the query with the specified configuration
        query_job = client.query(query, job_config=job_config)
        
        # Wait for the query to complete
        results = query_job.result()
        
        # Prepare the results as a list of dictionaries
        workouts = []
        for row in results:
            # Handle missing data by setting defaults (e.g., 0 for latitude/longitude or None)
            start_lat_lng = (
                row.StartLocationLat if row.StartLocationLat is not None else 0, 
                row.StartLocationLong if row.StartLocationLong is not None else 0
            )
            end_lat_lng = (
                row.EndLocationLat if row.EndLocationLat is not None else 0,
                row.EndLocationLong if row.EndLocationLong is not None else 0
            )
            
            workouts.append({
                'workout_id': row.WorkoutId,
                'start_timestamp': str(row.StartTimestamp),  # Ensure timestamps are strings
                'end_timestamp': str(row.EndTimestamp),
                'start_lat_lng': start_lat_lng,
                'end_lat_lng': end_lat_lng,
                'distance': row.TotalDistance,
                'steps': row.TotalSteps,
                'calories_burned': row.CaloriesBurned,
            })

        return workouts

    except Exception as e:
        raise Exception(f"Query failed: {str(e)}")


def get_user_profile(user_id):
    """
    AI Prompt:
    
    Write an AI prompt that would generate the Python function 
    get_user_profile(user_id) which retrieves profile information 
    (Name as 'full_name', Username as 'username', ImageUrl as 
    'profile_image', DateOfBirth as 'date_of_birth' in 'YYYY-MM-DD' format) 
    and a list of friends' UserIds ('friends') for a given user_id
    
    
    Returns information about the given user from BigQuery.

    Input: user_id
    Output: A single dictionary with the keys full_name, username, date_of_birth,
            profile_image, and friends (containing a list of friend user_ids)
    """

    # Explicitly set the project ID
    client = bigquery.Client(project="bamboo-creek-450920-h2")

    query = """
        SELECT
            Name,
            Username,
            ImageUrl,
            DateOfBirth
        FROM
            `bamboo-creek-450920-h2`.ISE.Users
        WHERE
            UserId = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    user_data = {}
    for row in results:
        user_data['full_name'] = row.Name
        user_data['username'] = row.Username
        user_data['profile_image'] = row.ImageUrl
        user_data['date_of_birth'] = row.DateOfBirth.strftime('%Y-%m-%d') if row.DateOfBirth else None

    if not user_data:
        raise ValueError(f'User {user_id} not found in the database.')

    # Fetch friends
    friends_query = """
        SELECT
            UserId2
        FROM
            `bamboo-creek-450920-h2`.ISE.Friends
        WHERE
            UserId1 = @user_id
    """
    friends_job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        ]
    )
    friends_query_job = client.query(friends_query, job_config=friends_job_config)
    friends_results = friends_query_job.result()

    user_data['friends'] = [row.UserId2 for row in friends_results]

    return user_data


def calculate_streak(workouts):
    """
    AI Prompt:
    Write a Python function calculate_streak(workouts) that determines both current and longest workout streaks from a list of workout data. The function should count consecutive workout days and return a tuple of integers representing the current streak and the all-time longest streak.
    
    If not workouts:
        return 0, 0
    """
    if not workouts:
        return 0, 0

    # Convert timestamps to dates
    workout_dates = sorted(set([datetime.fromisoformat(w['start_timestamp']).date() for w in workouts]))

    current_streak = 1
    longest_streak = 1
    streak = 1

    for i in range(1, len(workout_dates)):
        if (workout_dates[i] - workout_dates[i - 1]).days == 1:
            streak += 1
        else:
            streak = 1
        longest_streak = max(longest_streak, streak)

    # Check if the most recent date is yesterday or today
    last_workout = workout_dates[-1]
    today = datetime.now().date()
    if (today - last_workout).days in [0, 1]:
        current_streak = streak
    else:
        current_streak = 0

    return current_streak, longest_streak

def get_badges(workouts, current_streak, longest_streak):
    """
    AI Prompt:
    Write a Python function get_badges(workouts, current_streak, longest_streak) that awards achievement badges based on workout history and streak data. The function should return a list of strings representing earned badges for streaks, workout counts, and step milestones.
    """
    badges = []

    if current_streak >= 3:
        badges.append("3-Day Streak")
    if current_streak >= 7:
        badges.append("7-Day Streak")
    if longest_streak >= 14:
        badges.append("14-Day Warrior")
    if len(workouts) >= 10:
        badges.append("10 Workouts Complete")
    if len(workouts) >= 50:
        badges.append("50 Workouts Legend")
    total_steps = sum(workout.get('steps', 0) for workout in workouts)
    if total_steps >= 7000:
        badges.append("Walked a 5k")
    if total_steps >= 14000:
        badges.append("Walked a 10k")
    if total_steps >= 21000:
        badges.append("Walked a 15k")
    if total_steps >= 30000:
        badges.append("Walked a Half-Marathon")
    if total_steps >= 60000:
        badges.append("Walked a Marathon")

    return badges

def get_workout_stats(user_id):
    """
    AI Prompt:
    Write a Python function get_workout_stats(user_id) that retrieves comprehensive workout statistics for a user. The function should calculate current streak, longest streak, earned badges, and total workout count by calling other helper functions and return a dictionary with these statistics.
    """
    workouts = get_user_workouts(user_id)  # Already fetched data
    current_streak, longest_streak = calculate_streak(workouts)
    badges = get_badges(workouts, current_streak, longest_streak)

    return {
        "currentStreak": current_streak,
        "longestStreak": longest_streak,
        "badgeList": badges,
        "totalWorkouts": len(workouts)
    }


def get_user_posts(user_id):
    """
    AI Prompt:
    Write an AI prompt that would generate the Python function 
    get_user_posts(user_id) which retrieves a list of posts for 
    a given user_id from the BigQuery table
    
    
    Returns a list of a user's posts from BigQuery.

    Input: user_id
    Output: A list of posts. Each post is a dictionary with keys user_id,
            post_id, timestamp, content, and image.
    """

    # Explicitly set the project ID
    client = bigquery.Client(project="bamboo-creek-450920-h2")
    
    query = """
        SELECT
            PostId,
            Timestamp,
            ImageUrl,
            Content
        FROM
            `bamboo-creek-450920-h2`.ISE.Posts
        WHERE
            AuthorId = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    posts = []
    for row in results:
        posts.append({
            'user_id': user_id,
            'post_id': row.PostId,
            'timestamp': row.Timestamp.strftime('%Y-%m-%d %H:%M:%S') if row.Timestamp else None,
            'content': row.Content,
            'image': row.ImageUrl,
        })

    return posts



def get_genai_advice(user_id):
    """
    AI Prompt:
    
    Write an AI prompt that would generate the Python function 
    get_genai_advice(user_id) which retrieves a user's workout 
    and sensor data from BigQuery tables bamboo-creek-450920-h2.ISE.Workouts, 
    bamboo-creek-450920-h2.ISE.SensorData, and bamboo-creek-450920-h2.ISE.SensorTypes
    
    
    Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    
    client = bigquery.Client(project='bamboo-creek-450920-h2')
    # Initialize Vertex AI
    vertexai.init(project="bamboo-creek-450920-h2", location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-002")
    
    advice_query = f"""
        SELECT
            Workouts.WorkoutId,
            Workouts.UserId,
            Workouts.StartTimestamp,
            Workouts.EndTimestamp,
            Workouts.StartLocationLat,
            Workouts.StartLocationLong,
            Workouts.EndLocationLat,
            Workouts.EndLocationLong,
            Workouts.TotalDistance,
            Workouts.TotalSteps,
            Workouts.CaloriesBurned,
            SensorData.SensorId,
            SensorData.Timestamp,
            SensorData.SensorValue,
            SensorTypes.Name,
            SensorTypes.Units
        FROM
            `bamboo-creek-450920-h2`.`ISE`.`Workouts` AS Workouts
            INNER JOIN `bamboo-creek-450920-h2`.`ISE`.`SensorData` AS SensorData ON Workouts.WorkoutId = SensorData.WorkoutID
            INNER JOIN `bamboo-creek-450920-h2`.`ISE`.`SensorTypes` AS SensorTypes ON SensorData.SensorId = SensorTypes.SensorId
        WHERE Workouts.UserId = '{user_id}';
        """
    
    query_job = client.query(advice_query)
    results = query_job.result()
    
    # Process and structure the data
    user_data = {
    "user_id": user_id,
    "workouts": {}
    }
    
    for row in results:
        workout_id = row.WorkoutId
        
        if workout_id not in user_data["workouts"]:
            user_data["workouts"][workout_id] = {
                "workout_id": workout_id,
                "start_timestamp": str(row.StartTimestamp),
                "end_timestamp": str(row.EndTimestamp),
                "start_location": {"lat": row.StartLocationLat, "long": row.StartLocationLong},
                "end_location": {"lat": row.EndLocationLat, "long": row.EndLocationLong},
                "total_distance": row.TotalDistance,
                "total_steps": row.TotalSteps,
                "calories_burned": row.CaloriesBurned,
                "sensor_readings": []
            }
        
        sensor_reading = {
            "sensor_id": row.SensorId,
            "name": row.Name,
            "timestamp": str(row.Timestamp),
            "value": row.SensorValue,
            "units": row.Units
        }
        
        user_data["workouts"][workout_id]["sensor_readings"].append(sensor_reading)


    # Create prompt for the LLM with clear instructions
    prompt = f"""
    You are a fitness coach providing personalized advice based on workout data.
    Please analyze this user's workout information and provide ONE specific, actionable advice.

    USER DATA:
    {json.dumps(user_data, indent=2)}

    INSTRUCTIONS:
    1. Analyze the workout duration, distance, steps, and calories burned
    2. Look at the heart rate, step count, and temperature sensor readings
    3. Provide specific advice based on this data
    4. Focus on improving performance, recovery, and overall fitness
    5. The advice should be 2-3 sentences maximum
    6. DO NOT include any introductions or explanations about the data
    7. DO NOT mention that you're an AI or that you're analyzing data
    8. Return ONLY the advice text, nothing else
    9. Provide ONLY ONE specific piece of advice based on this data

    Your advice should sound like it's coming directly from a fitness coach to the user.
    """

    # Generate the advice using the model
    response = model.generate_content(prompt)
    advice = response.text.strip()
    
    image_query = f"""
        SELECT
        Images.ImageURL
        FROM
        `bamboo-creek-450920-h2`.`ISE`.`Images` AS Images;
        """
    
    query_job = client.query(image_query)
    results = query_job.result()
    
    images = []
    for row in results:
        images.append(row.ImageURL)
    images.append(None)
    
    image = random.choice(images)
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return {
        'advice_id': 'advice1',
        'timestamp': current_time,
        'content': advice,
        'image': image,
    }


def get_users():
    """
    AI Prompt:
    Write an AI prompt that would generate the Python function 
    get_users() which retrieves all user data (UserId, Name, 
    Username, ImageUrl, DateOfBirth) from the BigQuery table 
    bamboo-creek-450920-h2.ISE.Users
    
    
    Fetches user data from BigQuery and returns a list of dictionaries.
    Each dictionary represents a user with keys: 'UserId', 'Name', 'Username', 'ImageUrl', 'DateOfBirth'.
    """
    # Use the cached client
    client = get_bigquery_client()

    # Define the SQL query to fetch user data
    query = """
        SELECT UserId, Name, Username, ImageUrl, DateOfBirth
        FROM `bamboo-creek-450920-h2.ISE.Users`
    """
    
    # Run the query
    query_job = client.query(query)

    # Fetch results and convert them to a list of dictionaries
    results = query_job.result()
    
    # Prepare a list of dictionaries representing the users
    users = []
    for row in results:
        users.append({
            'UserId': row.UserId,
            'Name': row.Name,
            'Username': row.Username,
            'ImageUrl': row.ImageUrl,
            'DateOfBirth': str(row.DateOfBirth)  # Ensure DateOfBirth is in string format
        })

    return users


def get_user_water_intake(user_id, date=None):
    """
    AI Prompt:
    Write a Python function get_user_water_intake(user_id, date=None) that fetches water intake records from the BigQuery table ISE.WaterIntake for a specific user on a given date. If no date is provided, it should default to the current day and return records sorted by intake time.
    
    Fetches water intake records for a specific user on a specific date.
    If date is None, fetches records for the current day.
    
    Args:
        user_id (str): The user ID to fetch water intake for
        date (datetime, optional): The date to fetch records for. Defaults to today.
    
    Returns:
        List of dictionaries with water intake records
    """
    if date is None:
        date = datetime.now().date()
    
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query
    query = """
        SELECT 
            water_id,
            amount_ml,
            intake_time
        FROM `bamboo-creek-450920-h2.ISE.WaterIntake`
        WHERE user_id = @user_id
        AND DATE(intake_time) = @date
        ORDER BY intake_time DESC
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("date", "DATE", date),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Prepare the results
        water_records = []
        for row in results:
            water_records.append({
                'water_id': row.water_id,
                'amount_ml': row.amount_ml,
                'intake_time': row.intake_time.isoformat(),
            })
        
        return water_records
    
    except Exception as e:
        print(f"Error fetching water intake data: {str(e)}")
        return []

def add_water_intake(user_id, amount_ml, intake_time=None):
    """
    AI Prompt:
    Write a Python function add_water_intake(user_id, amount_ml, intake_time=None) that creates a new water intake record in the BigQuery table ISE.WaterIntake for a user with a specified amount in milliliters. The function should generate a unique ID for the record and return a boolean indicating success or failure.
    
    Adds a new water intake record for a user.
    
    Args:
        user_id (str): The user ID to add water intake for
        amount_ml (int): The amount of water in milliliters
        intake_time (datetime, optional): The time of intake. Defaults to now.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if intake_time is None:
        intake_time = datetime.now()
    
    # Generate a unique water_id
    water_id = f"water_{user_id}_{int(datetime.now().timestamp())}"
    
    # Initialize the BigQuery client
    client = bigquery.Client(project="bamboo-creek-450920-h2")
    
    # Define the SQL query for insertion
    query = """
        INSERT INTO `bamboo-creek-450920-h2.ISE.WaterIntake` 
        (water_id, user_id, amount_ml, intake_time)
        VALUES (@water_id, @user_id, @amount_ml, @intake_time)
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("water_id", "STRING", water_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("amount_ml", "INT64", amount_ml),
            bigquery.ScalarQueryParameter("intake_time", "TIMESTAMP", intake_time),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        return True
    
    except Exception as e:
        print(f"Error adding water intake: {str(e)}")
        return False

def get_daily_water_summary(user_id, days=7):
    """
    AI Prompt:
    Write a Python function get_daily_water_summary(user_id, days=7) that retrieves a summary of water intake over a specified number of days from the BigQuery table ISE.WaterIntake. The function should return a list of dictionaries with dates and total water intake, including zero values for days with no records.
    
    Gets a summary of water intake over the last specified number of days.
    
    Args:
        user_id (str): The user ID to fetch water intake for
        days (int): Number of days to include in the summary
    
    Returns:
        List of dictionaries with date and total water intake
    """
    # Calculate the start date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query
    query = """
        SELECT 
            DATE(intake_time) as date,
            SUM(amount_ml) as total_amount_ml
        FROM `bamboo-creek-450920-h2.ISE.WaterIntake`
        WHERE user_id = @user_id
        AND DATE(intake_time) BETWEEN @start_date AND @end_date
        GROUP BY DATE(intake_time)
        ORDER BY date ASC
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Prepare the results
        daily_summary = []
        for row in results:
            daily_summary.append({
                'date': row.date.strftime('%Y-%m-%d'),
                'total_ml': row.total_amount_ml,
            })
        
        # Fill in missing dates with zero intake
        all_dates = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            all_dates[date_str] = 0
            current_date += timedelta(days=1)
        
        # Update with actual data
        for entry in daily_summary:
            all_dates[entry['date']] = entry['total_ml']
        
        # Convert back to list format
        complete_summary = [
            {'date': date, 'total_ml': total_ml}
            for date, total_ml in all_dates.items()
        ]
        
        return complete_summary
    
    except Exception as e:
        print(f"Error fetching water intake summary: {str(e)}")
        return []

def get_nutrition_data(user_id, days=30):
    """
    AI Prompt:
    Write a Python function get_nutrition_data(user_id, days=30) that fetches nutrition summary data for a specified time period from the BigQuery table ISE.DailyNutritionSummary. The function should query daily nutrition totals including calories, macronutrients, and water intake for the given user.
    
    Fetches nutrition data for a user over a specified period of days
    
    Args:
        user_id (str): The user ID to fetch nutrition data for
        days (int): Number of days to include in the query
    
    Returns:
        List of dictionaries with daily nutrition data
    """
    # Calculate the start date
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query for daily nutrition data
    query = """
        SELECT 
            date,
            total_calories,
            total_protein,
            total_carbs,
            total_fat,
            total_water_ml
        FROM `bamboo-creek-450920-h2.ISE.DailyNutritionSummary`
        WHERE user_id = @user_id
        AND date BETWEEN @start_date AND @end_date
        ORDER BY date ASC
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Prepare the results
        nutrition_data = []
        for row in results:
            nutrition_data.append({
                'date': row.date.strftime('%Y-%m-%d'),
                'total_calories': row.total_calories,
                'total_protein': row.total_protein,
                'total_carbs': row.total_carbs,
                'total_fat': row.total_fat,
                'total_water_ml': row.total_water_ml,
            })
        
        return nutrition_data
    
    except Exception as e:
        print(f"Error fetching nutrition data: {str(e)}")
        return []

def get_meal_details(user_id, days=30):
    """
    AI Prompt:
    Write a Python function get_meal_details(user_id, days=30) that retrieves detailed meal and food information for a user from BigQuery tables ISE.Meals, ISE.MealFoods, and ISE.FoodItems. The function should join these tables to return comprehensive meal data including nutritional content for each food consumed.
    
    Fetches detailed meal data for a user over a specified period of days
    
    Args:
        user_id (str): The user ID to fetch meal data for
        days (int): Number of days to include in the query
    
    Returns:
        List of dictionaries with meal details
    """
    # Calculate the start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Use the cached client instead of creating a new one
    client = get_bigquery_client()
    
    # Define the SQL query for meal details
    query = """
        SELECT 
            m.meal_id,
            m.meal_type,
            m.meal_name,
            m.meal_time,
            f.food_name,
            f.brand_name,
            mf.quantity,
            mf.total_calories,
            mf.total_protein_grams,
            mf.total_carbs_grams,
            mf.total_fat_grams
        FROM `bamboo-creek-450920-h2.ISE.Meals` m
        JOIN `bamboo-creek-450920-h2.ISE.MealFoods` mf ON m.meal_id = mf.meal_id
        JOIN `bamboo-creek-450920-h2.ISE.FoodItems` f ON mf.food_id = f.food_id
        WHERE m.user_id = @user_id
        AND m.meal_time BETWEEN @start_date AND @end_date
        ORDER BY m.meal_time DESC
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
            bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Prepare the results
        meal_data = []
        for row in results:
            meal_data.append({
                'meal_id': row.meal_id,
                'meal_type': row.meal_type,
                'meal_name': row.meal_name,
                'meal_time': row.meal_time.isoformat(),
                'food_name': row.food_name,
                'brand_name': row.brand_name,
                'quantity': row.quantity,
                'total_calories': row.total_calories,
                'total_protein_grams': row.total_protein_grams,
                'total_carbs_grams': row.total_carbs_grams,
                'total_fat_grams': row.total_fat_grams,
            })
        
        return meal_data
    
    except Exception as e:
        print(f"Error fetching meal details: {str(e)}")
        return []
        
def get_performance_metrics(user_id, days=30):
    """
    AI Prompt:
    Write a Python function get_performance_metrics(user_id, days=30) that retrieves workout performance data for a user within a specified time period. The function should filter workout data by date range and add a formatted date field to each workout record for easier correlation with other data.
    
    Fetches workout performance metrics for a user over a specified period
    
    Args:
        user_id (str): The user ID to fetch performance data for
        days (int): Number of days to include in the query
    
    Returns:
        List of dictionaries with workout performance metrics
    """
    # Get workouts for the user
    workouts = get_user_workouts(user_id)
    
    # Filter workouts by date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    filtered_workouts = []
    for workout in workouts:
        workout_date = datetime.fromisoformat(workout['start_timestamp'])
        if start_date <= workout_date <= end_date:
            # Add date for easier correlation
            workout_date_str = workout_date.date().strftime('%Y-%m-%d')
            workout['date'] = workout_date_str
            filtered_workouts.append(workout)
    
    return filtered_workouts

def get_nutrition_performance_correlation(user_id, days=30):
    """
    AI Prompt:
    Write a Python function get_nutrition_performance_correlation(user_id, days=30) that combines nutrition and workout performance data for correlation analysis. The function should create a date-indexed dictionary containing both nutrition and workout data to enable analysis of relationships between diet and exercise performance.
    
    Fetches combined nutrition and performance data for correlation analysis
    
    Args:
        user_id (str): The user ID to fetch data for
        days (int): Number of days to include in the analysis
    
    Returns:
        Dictionary with nutrition and performance data by date
    """
    # Get nutrition data
    nutrition_data = get_nutrition_data(user_id, days)
    
    # Get performance data
    performance_data = get_performance_metrics(user_id, days)
    
    # Create a date index for both datasets
    correlated_data = {}
    
    # Index nutrition data by date
    for entry in nutrition_data:
        date = entry['date']
        correlated_data[date] = {
            'nutrition': entry,
            'performance': None
        }
    
    # Match performance data to dates
    for workout in performance_data:
        date = workout['date']
        if date in correlated_data:
            correlated_data[date]['performance'] = workout
        else:
            correlated_data[date] = {
                'nutrition': None,
                'performance': workout
            }
    
    return correlated_data

def add_meal(user_id, meal_type, meal_name=None, meal_time=None):
    """
    AI Prompt:
    Write a Python function add_meal(user_id, meal_type, meal_name=None, meal_time=None) that creates a new meal record in the BigQuery table ISE.Meals. The function should generate a unique meal ID, use the current time if no meal time is provided, and return the meal ID on success or None on failure.
    
    Adds a new meal record for a user
    
    Args:
        user_id (str): The user ID
        meal_type (str): Type of meal (breakfast, lunch, dinner, snack)
        meal_name (str, optional): Optional name for the meal
        meal_time (datetime, optional): Time of the meal. Defaults to current time
        
    Returns:
        str: The ID of the newly created meal if successful, None otherwise
    """
    if meal_time is None:
        meal_time = datetime.now()
    
    # Generate a unique meal_id
    meal_id = f"meal_{user_id}_{int(datetime.now().timestamp())}"
    
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query for insertion
    query = """
        INSERT INTO `bamboo-creek-450920-h2.ISE.Meals` 
        (meal_id, user_id, meal_type, meal_name, meal_time)
        VALUES (@meal_id, @user_id, @meal_type, @meal_name, @meal_time)
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("meal_id", "STRING", meal_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("meal_type", "STRING", meal_type),
            bigquery.ScalarQueryParameter("meal_name", "STRING", meal_name),
            bigquery.ScalarQueryParameter("meal_time", "TIMESTAMP", meal_time),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        return meal_id
    
    except Exception as e:
        print(f"Error adding meal: {str(e)}")
        return None

def add_food_to_meal(meal_id, food_id, quantity):
    """
    AI Prompt:
    Write a Python function add_food_to_meal(meal_id, food_id, quantity) that adds a food item to a meal in the BigQuery table ISE.MealFoods. The function should calculate total nutritional values based on the quantity, generate a unique ID for the meal-food relationship, and update daily nutrition summaries after adding the food.
    
    Adds a food item to a meal with the specified quantity
    
    Args:
        meal_id (str): The meal ID to add the food to
        food_id (str): The food ID to add
        quantity (float): The quantity/servings of the food
        
    Returns:
        bool: True if successful, False otherwise
    """
    # First, get the food item details to calculate total nutrients
    food_item = get_food_item(food_id)
    
    if not food_item:
        print(f"Error: Food item {food_id} not found")
        return False
    
    # Calculate the total nutrients based on quantity
    total_calories = food_item['calories'] * quantity
    total_protein = food_item['protein_grams'] * quantity
    total_carbs = food_item['carbs_grams'] * quantity
    total_fat = food_item['fat_grams'] * quantity
    
    # Generate a unique meal_food_id
    meal_food_id = f"mf_{meal_id}_{food_id}_{int(datetime.now().timestamp())}"
    
    # Initialize the BigQuery client
    client = bigquery.Client(project="bamboo-creek-450920-h2")
    
    # Define the SQL query for insertion
    query = """
        INSERT INTO `bamboo-creek-450920-h2.ISE.MealFoods` 
        (meal_food_id, meal_id, food_id, quantity, total_calories, 
         total_protein_grams, total_carbs_grams, total_fat_grams, added_at)
        VALUES (@meal_food_id, @meal_id, @food_id, @quantity, @total_calories, 
                @total_protein, @total_carbs, @total_fat, @added_at)
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("meal_food_id", "STRING", meal_food_id),
            bigquery.ScalarQueryParameter("meal_id", "STRING", meal_id),
            bigquery.ScalarQueryParameter("food_id", "STRING", food_id),
            bigquery.ScalarQueryParameter("quantity", "FLOAT64", quantity),
            bigquery.ScalarQueryParameter("total_calories", "FLOAT64", total_calories),
            bigquery.ScalarQueryParameter("total_protein", "FLOAT64", total_protein),
            bigquery.ScalarQueryParameter("total_carbs", "FLOAT64", total_carbs),
            bigquery.ScalarQueryParameter("total_fat", "FLOAT64", total_fat),
            bigquery.ScalarQueryParameter("added_at", "TIMESTAMP", datetime.now()),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        
        # Update the daily nutrition summary
        update_daily_nutrition_summary(meal_id)
        
        return True
    
    except Exception as e:
        print(f"Error adding food to meal: {str(e)}")
        return False

def get_user_meals(user_id, date=None):
    """
    AI Prompt:
    Write a Python function get_user_meals(user_id, date=None) that retrieves meal records with nutritional totals from BigQuery tables ISE.Meals and ISE.MealFoods for a specific user and date. The function should return a list of meals with calculated nutritional totals for each meal.
    
    Gets all meals for a user for a specific date
    
    Args:
        user_id (str): The user ID
        date (date, optional): The date to get meals for. Defaults to today.
        
    Returns:
        list: List of meal dictionaries with nutritional information
    """
    # Set default date to today if not provided
    if date is None:
        date = datetime.now().date()
    
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query to get meals with their nutritional totals
    query = """
        SELECT 
            m.meal_id,
            m.meal_type,
            m.meal_name,
            m.meal_time,
            SUM(mf.total_calories) as calories,
            SUM(mf.total_protein_grams) as protein_grams,
            SUM(mf.total_carbs_grams) as carbs_grams,
            SUM(mf.total_fat_grams) as fat_grams
        FROM 
            `bamboo-creek-450920-h2.ISE.Meals` m
        LEFT JOIN 
            `bamboo-creek-450920-h2.ISE.MealFoods` mf ON m.meal_id = mf.meal_id
        WHERE 
            m.user_id = @user_id
            AND DATE(m.meal_time) = @date
        GROUP BY
            m.meal_id, m.meal_type, m.meal_name, m.meal_time
        ORDER BY 
            m.meal_time
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("date", "DATE", date),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Process the results
        meals = []
        for row in results:
            meals.append({
                'meal_id': row.meal_id,
                'meal_type': row.meal_type,
                'meal_name': row.meal_name,
                'meal_time': row.meal_time.isoformat() if row.meal_time else None,
                'calories': row.calories or 0,
                'protein_grams': row.protein_grams or 0,
                'carbs_grams': row.carbs_grams or 0,
                'fat_grams': row.fat_grams or 0
            })
        
        return meals
    
    except Exception as e:
        print(f"Error getting user meals: {str(e)}")
        return []

def get_food_item(food_id):
    """
    AI Prompt:
    Write a Python function get_food_item(food_id) that retrieves detailed information about a specific food item from the BigQuery table ISE.FoodItems. The function should return a complete nutritional profile including serving size, calories, macronutrients, and micronutrients as a dictionary.
    
    Gets details for a specific food item
    
    Args:
        food_id (str): The ID of the food item
        
    Returns:
        dict: Food item details if found, None otherwise
    """
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query
    query = """
        SELECT 
            food_id,
            food_name,
            brand_name,
            serving_size_grams,
            calories,
            protein_grams,
            carbs_grams,
            fat_grams,
            fiber_grams,
            sugar_grams,
            sodium_mg
        FROM `bamboo-creek-450920-h2.ISE.FoodItems`
        WHERE food_id = @food_id
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("food_id", "STRING", food_id),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Get the first (and should be only) result
        for row in results:
            return {
                'food_id': row.food_id,
                'food_name': row.food_name,
                'brand_name': row.brand_name,
                'serving_size_grams': row.serving_size_grams,
                'calories': row.calories,
                'protein_grams': row.protein_grams,
                'carbs_grams': row.carbs_grams,
                'fat_grams': row.fat_grams,
                'fiber_grams': row.fiber_grams,
                'sugar_grams': row.sugar_grams,
                'sodium_mg': row.sodium_mg,
            }
        
        return None
    
    except Exception as e:
        print(f"Error fetching food item: {str(e)}")
        return None

def search_food_items(query=None, limit=50):
    """
    AI Prompt:
    Write a Python function search_food_items(query=None, limit=50) that searches for food items in the BigQuery table ISE.FoodItems based on a text query. The function should perform a case-insensitive search in both food name and brand name fields and return a limited list of matching food items.
    
    Searches for food items in the database
    
    Args:
        query (str, optional): Search query for food name or brand
        limit (int, optional): Maximum number of results to return
        
    Returns:
        list: List of food items matching the query
    """
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query
    if query:
        sql_query = """
            SELECT 
                food_id,
                food_name,
                brand_name,
                serving_size_grams,
                calories,
                protein_grams,
                carbs_grams,
                fat_grams
            FROM `bamboo-creek-450920-h2.ISE.FoodItems`
            WHERE LOWER(food_name) LIKE LOWER(@query)
                OR LOWER(brand_name) LIKE LOWER(@query)
            ORDER BY food_name
            LIMIT @limit
        """
        
        # Configure query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("query", "STRING", f"%{query}%"),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
    else:
        sql_query = """
            SELECT 
                food_id,
                food_name,
                brand_name,
                serving_size_grams,
                calories,
                protein_grams,
                carbs_grams,
                fat_grams
            FROM `bamboo-creek-450920-h2.ISE.FoodItems`
            ORDER BY food_name
            LIMIT @limit
        """
        
        # Configure query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
    
    try:
        # Execute the query
        query_job = client.query(sql_query, job_config=job_config)
        results = query_job.result()
        
        # Prepare the results
        food_items = []
        for row in results:
            food_items.append({
                'food_id': row.food_id,
                'food_name': row.food_name,
                'brand_name': row.brand_name,
                'serving_size_grams': row.serving_size_grams,
                'calories': row.calories,
                'protein_grams': row.protein_grams,
                'carbs_grams': row.carbs_grams,
                'fat_grams': row.fat_grams,
            })
        
        return food_items
    
    except Exception as e:
        print(f"Error searching food items: {str(e)}")
        return []

def get_all_food_items(limit=100):
    """
    AI Prompt:
    Write a Python function get_all_food_items(limit=100) that retrieves a list of food items from the BigQuery table ISE.FoodItems for user selection. The function should return essential information including ID, name, brand, and nutritional content, with formatted display names combining food and brand names.
    
    Gets all food items from the database for selection
    
    Args:
        limit (int, optional): Maximum number of results to return. Defaults to 100.
        
    Returns:
        list: List of food item dictionaries with id, name, and brand for the UI selector
    """
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query to get all food items
    query = """
        SELECT 
            food_id,
            food_name,
            brand_name,
            calories,
            protein_grams,
            carbs_grams,
            fat_grams
        FROM `bamboo-creek-450920-h2.ISE.FoodItems`
        ORDER BY food_name
        LIMIT @limit
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Prepare the results
        food_items = []
        for row in results:
            # Format display name as "Food Name (Brand Name)"
            brand_text = f" ({row.brand_name})" if row.brand_name else ""
            food_display = f"{row.food_name}{brand_text}"
            
            # Return all necessary information
            food_items.append({
                'food_id': row.food_id,
                'display_name': food_display,
                'food_name': row.food_name,
                'brand_name': row.brand_name,
                'calories': row.calories,
                'protein_grams': row.protein_grams,
                'carbs_grams': row.carbs_grams,
                'fat_grams': row.fat_grams
            })
        
        return food_items
    
    except Exception as e:
        print(f"Error fetching all food items: {str(e)}")
        return []

def add_custom_food_item(food_name, brand_name, serving_size_grams, calories, 
                         protein_grams, carbs_grams, fat_grams, fiber_grams=0, 
                         sugar_grams=0, sodium_mg=0):
    """
    AI Prompt:
    Write a Python function add_custom_food_item() that adds a user-defined food item to the BigQuery table ISE.FoodItems with complete nutritional information. The function should generate a unique food ID, insert the record, and return the ID on success or None on failure.
    
    Adds a custom food item to the database
    
    Args:
        food_name (str): Name of the food
        brand_name (str): Brand of the food
        serving_size_grams (float): Serving size in grams
        calories (float): Calories per serving
        protein_grams (float): Protein in grams per serving
        carbs_grams (float): Carbohydrates in grams per serving
        fat_grams (float): Fat in grams per serving
        fiber_grams (float, optional): Fiber in grams per serving
        sugar_grams (float, optional): Sugar in grams per serving
        sodium_mg (float, optional): Sodium in milligrams per serving
        
    Returns:
        str: The ID of the newly created food item if successful, None otherwise
    """
    # Generate a unique food_id
    food_id = f"food_{int(datetime.now().timestamp())}"
    
    # Use the cached client
    client = get_bigquery_client()
    
    # Define the SQL query for insertion
    query = """
        INSERT INTO `bamboo-creek-450920-h2.ISE.FoodItems` 
        (food_id, food_name, brand_name, serving_size_grams, calories, 
         protein_grams, carbs_grams, fat_grams, fiber_grams, sugar_grams, sodium_mg)
        VALUES (@food_id, @food_name, @brand_name, @serving_size_grams, @calories, 
                @protein_grams, @carbs_grams, @fat_grams, @fiber_grams, @sugar_grams, @sodium_mg)
    """
    
    # Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("food_id", "STRING", food_id),
            bigquery.ScalarQueryParameter("food_name", "STRING", food_name),
            bigquery.ScalarQueryParameter("brand_name", "STRING", brand_name),
            bigquery.ScalarQueryParameter("serving_size_grams", "FLOAT64", serving_size_grams),
            bigquery.ScalarQueryParameter("calories", "FLOAT64", calories),
            bigquery.ScalarQueryParameter("protein_grams", "FLOAT64", protein_grams),
            bigquery.ScalarQueryParameter("carbs_grams", "FLOAT64", carbs_grams),
            bigquery.ScalarQueryParameter("fat_grams", "FLOAT64", fat_grams),
            bigquery.ScalarQueryParameter("fiber_grams", "FLOAT64", fiber_grams),
            bigquery.ScalarQueryParameter("sugar_grams", "FLOAT64", sugar_grams),
            bigquery.ScalarQueryParameter("sodium_mg", "FLOAT64", sodium_mg),
        ]
    )
    
    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for the query to complete
        return food_id
    
    except Exception as e:
        print(f"Error adding custom food item: {str(e)}")
        return None

def update_daily_nutrition_summary(meal_id):
    """
    AI Prompt:
    Write a Python function update_daily_nutrition_summary(meal_id) that updates the nutrition summary in BigQuery after a meal is added or modified. The function should retrieve the meal details, identify the user and date, and update the goal progress data accordingly for accurate nutrition tracking.
    
    Updates the daily nutrition summary for a user based on a newly added meal
    
    Args:
        meal_id (str): The ID of the meal that was added or modified
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Use the cached client
    client = get_bigquery_client()
    
    # First, get the meal details
    meal_query = """
        SELECT user_id, meal_time
        FROM `bamboo-creek-450920-h2.ISE.Meals`
        WHERE meal_id = @meal_id
    """
    
    meal_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("meal_id", "STRING", meal_id),
        ]
    )
    
    try:
        meal_job = client.query(meal_query, job_config=meal_config)
        meal_results = meal_job.result()
        
        # Get the user_id and date from the meal
        user_id = None
        meal_date = None
        
        for row in meal_results:
            user_id = row.user_id
            meal_date = row.meal_time.date()
        
        if not user_id or not meal_date:
            print("Could not find meal details")
            return False
        
        # Use our new update_goal_progress function to update the progress data
        return update_goal_progress(user_id, meal_date)
        
    except Exception as e:
        print(f"Error updating daily nutrition summary: {str(e)}")
        return False

def set_user_nutrition_goals(user_id, calorie_goal, goal_type='daily', start_date=None, end_date=None):
    """
    Set user nutrition (calorie) goals in the database
    
    Args:
        user_id (str): User ID
        calorie_goal (int): Daily calorie goal in kcal
        goal_type (str, optional): Type of goal ('daily', 'weekly', 'monthly'). Defaults to 'daily'.
        start_date (date, optional): Start date of the goal. Defaults to today.
        end_date (date, optional): End date of the goal. Can be None for ongoing goals.
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_bigquery_client()
        
        # Set default start date to today if not provided
        if start_date is None:
            start_date = datetime.now().date()
            
        # Create a unique goal_id
        goal_id = f"goal_{user_id}_{int(datetime.now().timestamp())}"
        
        # SQL query to insert a new goal
        query = """
        INSERT INTO `bamboo-creek-450920-h2.ISE.CalorieGoals`
        (goal_id, user_id, goal_type, calorie_target, start_date, end_date, created_at)
        VALUES 
        (@goal_id, @user_id, @goal_type, @calorie_target, @start_date, @end_date, CURRENT_TIMESTAMP())
        """
        
        # Set query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("goal_id", "STRING", goal_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("goal_type", "STRING", goal_type),
                bigquery.ScalarQueryParameter("calorie_target", "INTEGER", calorie_goal),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
        
        # Execute query
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # Wait for query to complete
        
        return True
        
    except Exception as e:
        print(f"Error setting calorie goals: {e}")
        return False


def get_user_nutrition_goals(user_id, date=None):
    """
    Get user nutrition (calorie) goals from the database
    
    Args:
        user_id (str): User ID
        date (date, optional): The date for which to get the goals. Defaults to today.
        
    Returns:
        dict: User's calorie goal or None if not found
    """
    try:
        client = get_bigquery_client()
        
        # Use today if no date specified
        if date is None:
            date = datetime.now().date()
        
        # SQL query to get user's active calorie goal for the specified date
        query = """
        SELECT 
            goal_id,
            goal_type,
            calorie_target,
            start_date,
            end_date,
            created_at
        FROM 
            `bamboo-creek-450920-h2.ISE.CalorieGoals` 
        WHERE 
            user_id = @user_id
            AND start_date <= @date
            AND (end_date IS NULL OR end_date >= @date)
        ORDER BY 
            created_at DESC
        LIMIT 1
        """
        
        # Set query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("date", "DATE", date)
            ]
        )
        
        # Execute query
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if not results:
            return None
            
        # Return first result as dictionary
        goal = results[0]
        return {
            "goal_id": goal.goal_id,
            "goal_type": goal.goal_type,
            "calorie_target": goal.calorie_target,
            "start_date": goal.start_date,
            "end_date": goal.end_date,
            "created_at": goal.created_at
        }
        
    except Exception as e:
        print(f"Error getting calorie goals: {e}")
        return None


def get_daily_nutrition_progress(user_id, date=None):
    """
    Get daily nutrition progress compared to goals
    
    Args:
        user_id (str): User ID
        date (str, optional): Date in format 'YYYY-MM-DD'. Defaults to today.
        
    Returns:
        dict: Nutrition progress with consumption and goals data
    """
    try:
        # Use today if no date specified
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(date, str):
            # Convert string to date object if needed
            date = datetime.strptime(date, '%Y-%m-%d').date()
            
        # Get goals for the specific date
        goals = get_user_nutrition_goals(user_id, date)
        if not goals:
            return None
            
        # Check if we already have progress data for this day
        client = get_bigquery_client()
        
        query = """
        SELECT 
            progress_id,
            goal_id,
            total_calories_consumed,
            calories_remaining,
            updated_at
        FROM 
            `bamboo-creek-450920-h2.ISE.GoalProgress`
        WHERE 
            user_id = @user_id
            AND date = @date
        ORDER BY
            updated_at DESC
        LIMIT 1
        """
        
        # Set query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("date", "DATE", date)
            ]
        )
        
        # Execute query
        query_job = client.query(query, job_config=job_config)
        progress_results = list(query_job.result())
        
        if progress_results:
            # Use the existing progress data
            progress = progress_results[0]
            
            # Calculate consumption and remaining values
            consumption = {
                "calories": progress.total_calories_consumed or 0
            }
            
            remaining = {
                "calories": progress.calories_remaining or 0
            }
            
            # Calculate progress percentage
            calories_percent = 0
            if goals["calorie_target"] > 0:
                calories_percent = min(100, (consumption["calories"] / goals["calorie_target"]) * 100)
            
            return {
                "goals": goals,
                "consumption": consumption,
                "date": date if isinstance(date, str) else date.strftime("%Y-%m-%d"),
                "progress": {
                    "calories_percent": calories_percent
                },
                "remaining": remaining,
                "updated_at": progress.updated_at
            }
        
        # If no progress data exists, we need to calculate it from meals data
        meal_query = """
        SELECT 
            SUM(total_calories) as calories_consumed
        FROM 
            `bamboo-creek-450920-h2.ISE.meal_foods`
        JOIN
            `bamboo-creek-450920-h2.ISE.meals` ON meal_foods.meal_id = meals.meal_id
        WHERE 
            meals.user_id = @user_id
            AND DATE(meals.meal_time) = @date
        """
        
        # Set query parameters
        meal_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("date", "DATE", date)
            ]
        )
        
        # Execute query
        meal_job = client.query(meal_query, job_config=meal_config)
        meal_results = list(meal_job.result())
        
        # Default values if no consumption data
        calories_consumed = 0
        if meal_results and meal_results[0].calories_consumed:
            calories_consumed = meal_results[0].calories_consumed
            
        # Calculate remaining calories
        calories_remaining = max(0, goals["calorie_target"] - calories_consumed)
        
        # Create progress entry
        progress_id = f"progress_{user_id}_{datetime.now().timestamp()}"
        
        # Insert progress data
        insert_query = """
        INSERT INTO `bamboo-creek-450920-h2.ISE.GoalProgress`
        (progress_id, goal_id, user_id, date, total_calories_consumed, calories_remaining, updated_at)
        VALUES
        (@progress_id, @goal_id, @user_id, @date, @calories_consumed, @calories_remaining, CURRENT_TIMESTAMP())
        """
        
        insert_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("progress_id", "STRING", progress_id),
                bigquery.ScalarQueryParameter("goal_id", "STRING", goals["goal_id"]),
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("date", "DATE", date),
                bigquery.ScalarQueryParameter("calories_consumed", "INTEGER", calories_consumed),
                bigquery.ScalarQueryParameter("calories_remaining", "INTEGER", calories_remaining)
            ]
        )
        
        # Execute insert query
        insert_job = client.query(insert_query, job_config=insert_config)
        insert_job.result()
        
        # Calculate progress percentage
        calories_percent = 0
        if goals["calorie_target"] > 0:
            calories_percent = min(100, (calories_consumed / goals["calorie_target"]) * 100)
        
        return {
            "goals": goals,
            "consumption": {
                "calories": calories_consumed
            },
            "date": date if isinstance(date, str) else date.strftime("%Y-%m-%d"),
            "progress": {
                "calories_percent": calories_percent
            },
            "remaining": {
                "calories": calories_remaining
            },
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        print(f"Error getting nutrition progress: {e}")
        return None


def get_weekly_nutrition_progress(user_id, days=7):
    """
    Get weekly nutrition progress compared to goals
    
    Args:
        user_id (str): User ID
        days (int, optional): Number of days to include. Defaults to 7.
        
    Returns:
        dict: Weekly nutrition progress data
    """
    try:
        # Calculate start date
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get progress data directly from GoalProgress table
        client = get_bigquery_client()
        
        query = """
        SELECT 
            date,
            goal_id,
            total_calories_consumed,
            calories_remaining,
            updated_at
        FROM 
            `bamboo-creek-450920-h2.ISE.GoalProgress`
        WHERE 
            user_id = @user_id
            AND date BETWEEN @start_date AND @end_date
        ORDER BY 
            date ASC
        """
        
        # Configure query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
        
        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Prepare daily progress data
        daily_progress = {}
        goal_ids = set()
        
        for row in results:
            daily_progress[row.date.strftime('%Y-%m-%d')] = {
                "date": row.date.strftime('%Y-%m-%d'),
                "goal_id": row.goal_id,
                "consumption": {
                    "calories": row.total_calories_consumed
                },
                "remaining": {
                    "calories": row.calories_remaining
                },
                "updated_at": row.updated_at
            }
            goal_ids.add(row.goal_id)
        
        # Fill in missing dates
        all_dates = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in daily_progress:
                # Get goal for this date
                goal = get_user_nutrition_goals(user_id, current_date)
                if goal:
                    # No progress entry yet, create one
                    progress = get_daily_nutrition_progress(user_id, current_date)
                    if progress:
                        daily_progress[date_str] = progress
            
            current_date += timedelta(days=1)
        
        # Convert to list and sort by date
        daily_progress_list = list(daily_progress.values())
        daily_progress_list.sort(key=lambda x: x["date"])
        
        # Calculate weekly averages
        if not daily_progress_list:
            return None
            
        # Calculate averages
        total_days = len(daily_progress_list)
        avg_calories = sum(day["consumption"]["calories"] for day in daily_progress_list) / total_days
        avg_calories_remaining = sum(day["remaining"]["calories"] for day in daily_progress_list) / total_days
        
        # Get current goal
        current_goal = get_user_nutrition_goals(user_id)
        if not current_goal:
            return {
                "daily_progress": daily_progress_list,
                "averages": {
                    "calories": avg_calories,
                    "calories_remaining": avg_calories_remaining
                }
            }
        
        # Calculate weekly progress percentage
        calories_percent = 0
        if current_goal["calorie_target"] > 0:
            calories_percent = min(100, (avg_calories / current_goal["calorie_target"]) * 100)
        
        return {
            "daily_progress": daily_progress_list,
            "averages": {
                "calories": avg_calories,
                "calories_remaining": avg_calories_remaining
            },
            "current_goal": current_goal,
            "progress": {
                "calories_percent": calories_percent
            }
        }
        
    except Exception as e:
        print(f"Error getting weekly nutrition progress: {e}")
        return None

def update_goal_progress(user_id, date=None, calories_consumed=None):
    """
    AI Prompt:
    Write a Python function update_goal_progress(user_id, date=None, calories_consumed=None) that updates nutrition goal progress in the BigQuery table ISE.GoalProgress. The function should calculate or use provided calorie consumption, determine remaining calories against goals, and either update existing records or create new ones.
    
    Updates the goal progress for a user on a specific date
    
    Args:
        user_id (str): User ID
        date (date, optional): Date to update progress for. Defaults to today.
        calories_consumed (int, optional): Total calories consumed. If None, will calculate from meals.
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use today if no date specified
        if date is None:
            date = datetime.now().date()
        elif isinstance(date, str):
            # Convert string to date object if needed
            date = datetime.strptime(date, '%Y-%m-%d').date()
            
        # Get goals for the specific date
        goals = get_user_nutrition_goals(user_id, date)
        if not goals:
            print(f"No calorie goal found for user {user_id} on {date}")
            return False
            
        client = get_bigquery_client()
        
        # If calories_consumed not provided, calculate from meals
        if calories_consumed is None:
            # Query to get calories consumed from meals
            meal_query = """
            SELECT 
                SUM(total_calories) as calories_consumed
            FROM 
                `bamboo-creek-450920-h2.ISE.meal_foods`
            JOIN
                `bamboo-creek-450920-h2.ISE.meals` ON meal_foods.meal_id = meals.meal_id
            WHERE 
                meals.user_id = @user_id
                AND DATE(meals.meal_time) = @date
            """
            
            # Set query parameters
            meal_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("date", "DATE", date)
                ]
            )
            
            # Execute query
            meal_job = client.query(meal_query, job_config=meal_config)
            meal_results = list(meal_job.result())
            
            # Default to 0 if no consumption data
            calories_consumed = 0
            if meal_results and meal_results[0].calories_consumed:
                calories_consumed = meal_results[0].calories_consumed
        
        # Calculate remaining calories
        calories_remaining = max(0, goals["calorie_target"] - calories_consumed)
        
        # Check if a progress record already exists
        check_query = """
        SELECT progress_id
        FROM `bamboo-creek-450920-h2.ISE.GoalProgress`
        WHERE user_id = @user_id AND date = @date
        """
        
        check_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("date", "DATE", date)
            ]
        )
        
        check_job = client.query(check_query, job_config=check_config)
        existing_records = list(check_job.result())
        
        if existing_records:
            # Update existing record
            progress_id = existing_records[0].progress_id
            update_query = """
            UPDATE `bamboo-creek-450920-h2.ISE.GoalProgress`
            SET 
                total_calories_consumed = @calories_consumed,
                calories_remaining = @calories_remaining,
                updated_at = CURRENT_TIMESTAMP()
            WHERE progress_id = @progress_id
            """
            
            update_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("progress_id", "STRING", progress_id),
                    bigquery.ScalarQueryParameter("calories_consumed", "INTEGER", calories_consumed),
                    bigquery.ScalarQueryParameter("calories_remaining", "INTEGER", calories_remaining)
                ]
            )
            
            update_job = client.query(update_query, job_config=update_config)
            update_job.result()
        else:
            # Create new progress record
            progress_id = f"progress_{user_id}_{int(datetime.now().timestamp())}"
            
            insert_query = """
            INSERT INTO `bamboo-creek-450920-h2.ISE.GoalProgress`
            (progress_id, goal_id, user_id, date, total_calories_consumed, calories_remaining, updated_at)
            VALUES
            (@progress_id, @goal_id, @user_id, @date, @calories_consumed, @calories_remaining, CURRENT_TIMESTAMP())
            """
            
            insert_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("progress_id", "STRING", progress_id),
                    bigquery.ScalarQueryParameter("goal_id", "STRING", goals["goal_id"]),
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("date", "DATE", date),
                    bigquery.ScalarQueryParameter("calories_consumed", "INTEGER", calories_consumed),
                    bigquery.ScalarQueryParameter("calories_remaining", "INTEGER", calories_remaining)
                ]
            )
            
            insert_job = client.query(insert_query, job_config=insert_config)
            insert_job.result()
        
        return True
        
    except Exception as e:
        print(f"Error updating goal progress: {e}")
        return False