"""
AI Prompt:
Write a Python script that generates test workout data for 10 users and inserts it 
into a BigQuery table named 'bamboo-creek-450920-h2.ISE.Workouts'. For each user, 
create 13 workout records with random duration, distance, steps, and calories, 
spanning the last 13 days from the current date. Use UUID for workout IDs and 
format the output to show success or error messages after insertion.
"""

from google.cloud import bigquery
from datetime import datetime, timedelta
import random
import uuid

# Initialize client
client = bigquery.Client(project="bamboo-creek-450920-h2")

# Reference the table
table_id = "bamboo-creek-450920-h2.ISE.Workouts"

# Generate test workouts for users 1–10
rows_to_insert = []
now = datetime.utcnow()

for i in range(1, 11):  # User1 to User10
    user_id = f"user{i}"
    for j in range(13):  # 5 workouts per user
        start = now - timedelta(days=j)
        end = start + timedelta(minutes=random.randint(30, 90))

        rows_to_insert.append({
            "WorkoutId": str(uuid.uuid4()),
            "UserId": user_id,
            "StartTimestamp": start.isoformat(),
            "EndTimestamp": end.isoformat(),
            "StartLocationLat": round(random.uniform(37.0, 38.0), 6),
            "StartLocationLong": round(random.uniform(-122.0, -121.0), 6),
            "EndLocationLat": round(random.uniform(37.0, 38.0), 6),
            "EndLocationLong": round(random.uniform(-122.0, -121.0), 6),
            "TotalDistance": round(random.uniform(1.0, 6.0), 2),  # in miles
            "TotalSteps": random.randint(3000, 12000),
            "CaloriesBurned": round(random.uniform(150.0, 600.0), 1),
        })

# Insert rows into BigQuery
errors = client.insert_rows_json(table_id, rows_to_insert)

if errors == []:
    print("✅ Successfully inserted test workout rows.")
else:
    print("❌ Errors occurred while inserting rows:")
    print(errors)
