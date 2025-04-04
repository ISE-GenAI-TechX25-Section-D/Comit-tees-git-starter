#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import random
from google.cloud import bigquery
from google.api_core import exceptions as google_exceptions
from datetime import datetime

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
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
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}


def get_user_sensor_data(client: bigquery.Client, user_id: str, workout_id: str):
    """Returns a list of timestampped information for a given workout.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    query_prompt = f"""
        SELECT SensorId, Timestamp, SensorValue
        FROM `diegoperez16techx25`.`Committees`.`SensorData`
        WHERE WorkoutID = '{workout_id}'
    """
    sensor_data_dictionaries = []
    try:
        # 1. Check if user_id exists
        user_check_query = f"""
            SELECT 1 FROM `diegoperez16techx25`.`Committees`.`Users`
            WHERE UserId = '{user_id}'
        """
        user_check_result = client.query(user_check_query).result()
        if not list(user_check_result):
            raise ValueError(f"User ID '{user_id}' not found.")

        # 2. Check if workout_id exists and is associated with user_id
        workout_check_query = f"""
            SELECT 1 FROM `diegoperez16techx25`.`Committees`.`Workouts`
            WHERE WorkoutId = '{workout_id}' AND UserId = '{user_id}'
        """
        workout_check_result = client.query(workout_check_query).result()
        if not list(workout_check_result):
            raise ValueError(f"Workout ID '{workout_id}' not found or not associated with user ID '{user_id}'.")

        query = client.query(query_prompt)
        results = query.result()  # Waits for query to finish

        for row in results:
            sensor_data_dictionaries.append({
                'SensorId': row.SensorId,
                'Timestamp': row.Timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Data': row.SensorValue,
            })
        if sensor_data_dictionaries:
            sensor_ids = [item['SensorId'] for item in sensor_data_dictionaries]
            sensor_types_query = f"""
                SELECT SensorId, Name, Units
                FROM `diegoperez16techx25`.`Committees`.`SensorTypes`
                WHERE SensorId IN UNNEST({sensor_ids})
            """
            sensor_types_results = client.query(sensor_types_query).result()

            # 3. Create a Sensor Type Map
            sensor_types_map = {row.SensorId: {'Sensor_type': row.Name, 'Units': row.Units} for row in sensor_types_results}

            # 4. Combine Data
            for item in sensor_data_dictionaries:
                sensor_id = item['SensorId']
                if sensor_id in sensor_types_map:
                    item.update(sensor_types_map[sensor_id])
                item.pop('SensorId')

        return sensor_data_dictionaries
    except google_exceptions.GoogleAPIError as e:
        raise  # Re-raise the BigQuery API error
    except ValueError as e:
        raise # Re-raise the value errors.
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []  # Return an empty list for other unexpected errors
    


def get_user_workouts(user_id, query_db=bigquery, execute_query=None):
    """Returns a list of user's workouts from the BigQuery database.
    """
    client = query_db.Client()
    query = f""" SELECT * FROM `diegoperez16techx25.Committees.Workouts` WHERE UserId = '{user_id}' """
    # run this line to authorize queries: gcloud auth application-default login
    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query
    
    results = execute_query(client, query)
    workouts = []
    for row in results:
        workouts.append({
            'workout_id': row[0],
            'start_timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S'),
            'end_timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S'),
            'start_lat_lng': (row[4], row[5]),
            'end_lat_lng': (row[6], row[7]),
            'distance': row[8],
            'steps': row[9],
            'calories_burned': row[10]
        })
    return workouts


def get_user_profile(user_id):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


def get_user_posts(user_id):
    """Returns a list of a user's posts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])
    return [{
        'user_id': user_id,
        'post_id': 'post1',
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSz0kSuHwimKiIaNdUXwlaLMlkmnTXVC36Qkg&s',
    }]


def get_genai_advice(user_id):
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }

