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
import os
import uuid
import json

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.vision_models import Image, ImageGenerationModel
from dotenv import load_dotenv
load_dotenv()
vertexai.init(project=os.environ.get("diegoperez16techx25"), location="us-central1")


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

#used gemini for assistance: 
def get_user_profile(user_id, query_db=bigquery, execute_query=None):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """

    client = query_db.Client()

    # Step 1: Get user info from the Users table
    query = f"""
        SELECT 
            Name,
            Username,
            ImageUrl,
            DateOfBirth
        FROM 
            `diegoperez16techx25.Committees.Users` 
        WHERE 
            UserId = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    if results.total_rows == 0:
        raise ValueError(f"User {user_id} not found.")

    row = list(results)[0]

    # Step 2: Get the user's friends
    friends = get_user_friends(user_id)

    # Step 3: Return nicely structured profile data
    return {
        "full_name": row[0],
        "username": row[1],
        "profile_image": row[2],
        "date_of_birth": row[3].strftime('%Y-%m-%d') if row[3] else None,
        "friends": friends
    }

#used gemini for assistance: 
def get_user_posts(user_id, query_db=bigquery, execute_query=None):
    """Returns a list of a user's posts from the BigQuery database."""
    client = query_db.Client()
    query = f"""
        SELECT 
            PostId,
            AuthorId,
            Timestamp,
            ImageUrl,
            Content
        FROM 
            `diegoperez16techx25.Committees.Posts` 
        WHERE 
            AuthorId = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    posts = []
    for row in results:
        posts.append({
            'post_id': row[0],
            'user_id': row[1],
            'timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S'),
            'image': row[3],
            'content': row[4],
        })
    return posts

def insert_user_post(user_id, content, image_url=None, query_db=bigquery, execute_query=None):
    """Inserts a new post into the Posts table in BigQuery for the given user, with custom post ID format like 'post4'."""
    client = query_db.Client()

    get_max_query = """
        SELECT MAX(CAST(SUBSTR(PostId, 5) AS INT64)) as max_id
        FROM `diegoperez16techx25.Committees.Posts`
        WHERE SAFE_CAST(SUBSTR(PostId, 5) AS INT64) IS NOT NULL
    """
    query_job = client.query(get_max_query)
    max_id_row = list(query_job.result())[0]
    max_id = max_id_row[0] or 0
    new_id = f"post{max_id + 1}"

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    content_escaped = content.replace("'", "''") 
    image_url = image_url or ''
    insert_query = f"""
        INSERT INTO `diegoperez16techx25.Committees.Posts`
        (PostId, AuthorId, Timestamp, ImageUrl, Content)
        VALUES (
            '{new_id}',
            '{user_id}',
            '{timestamp}',
            '{image_url}',
            '{content_escaped}'
        )
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    execute_query(client, insert_query)

#used gemini for assistance: 
def get_user_friends(user_id, query_db=bigquery, execute_query=None):
    """Returns a list of a user's friends from the BigQuery database."""
    client = query_db.Client()
    query = f"""
        SELECT 
            friend_id 
        FROM 
            `diegoperez16techx25.Committees.Friends` 
        WHERE 
            user_id = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    friends = [row[0] for row in results]
    return friends

def get_user_info(user_id, query_db=bigquery, execute_query=None):
    """Returns a user's profile information from the BigQuery database."""
    client = query_db.Client()
    query = f"""
        SELECT 
            Name,
            Username,
            ImageUrl
        FROM 
            `diegoperez16techx25.Committees.Users` 
        WHERE 
            UserId = '{user_id}'
    """

    if execute_query is None:
        def default_execute_query(client, query):
            query_job = client.query(query)
            return query_job.result()
        execute_query = default_execute_query

    results = execute_query(client, query)
    if results.total_rows > 0:
        row = next(iter(results))
        return {
            'full_name': row[0],
            'username': row[1],
            'profile_image': row[2],
        }
    else:
        return None


def get_genai_advice(user_id):
    """
    Generate fitness advice and motivational image based on user's workout history.
    
    Args:
        user_id: The ID of the user
        text_model: GenerativeModel instance (injected for testing)
        image_model: ImageGenerationModel instance (injected for testing)
        workouts_provider: Function to get workouts (injected for testing)
        timestamp: Optional timestamp (for testing)
    
    Returns:
        Dictionary containing advice_id, content, image filename, and timestamp
    """
    client = bigquery.Client()
    user_check_query = f"""
            SELECT 1 FROM `diegoperez16techx25`.`Committees`.`Users`
            WHERE UserId = '{user_id}'
        """
    user_check_result = client.query(user_check_query).result()
    if not list(user_check_result):
        raise ValueError(f"User ID '{user_id}' not found.")

    text_model = GenerativeModel(
        "gemini-1.5-flash-002", 
        system_instruction="You are a qualified fitness coach. You will take input the data from client which is a list of information from different workouts they did and then you will give me a 1-2 sentence advice based on this information."
    )
    
    image_model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    
    workouts_provider = get_user_workouts  # Default to your actual function
    
    timestamp = datetime.now()
    
    # Get workouts for the user
    try:
        workouts = workouts_provider(user_id)
    except Exception as e:
        print(f"❌ Workout retrieval failed: {e}")
        return None 
    
    result = {}
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "adviceid": {"type": "STRING", "description": "Unique identifier for the advice"},
            "advice": {"type": "STRING", "description": "The 1-2 sentence fitness advice"}
        },
        "required": ["adviceid", "advice"]
    }
    
    # Generate advice
    try:
        if workouts:
            advice_prompt = "Generate advice and an adviceid for this user based on this workout summary list: " + str(workouts)
        else:
            advice_prompt = "Give advice and an adviceid for this user, The user has no recorded workouts. Give a motivational message to start training"
        advice_response = text_model.generate_content(
            advice_prompt,
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema
            ),
        )
        
        structured_response = json.loads(advice_response.text)
        advice_id = structured_response.get("adviceid")
        advice_content = structured_response.get("advice")
        
        if not advice_id or not advice_content:
            raise ValueError("Invalid response from text model")
            
        result['advice_id'] = advice_id
        result['content'] = advice_content
    except Exception as e:
        print(f"Error generating advice: {e}")
        return None
    
    # Generate image
    try:
        image_prompt = f"Generate a motivational image based on this advice: {advice_content}, This image should serve as motivation for the user, avoid just bodychecking content."
        image_response = image_model.generate_images(
            prompt=image_prompt,
            number_of_images=1
        )
        
        if image_response and image_response.images:
            image = image_response.images[0]
            filename = f"motivation_{uuid.uuid4().hex}.png"
            image.save(filename)
            result['image'] = filename
        else:
            result['image'] = None
    except Exception as e:
        print(f"Error generating image: {e}")
        result['image'] = None
    
    # Add timestamp
    result['timestamp'] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    return result
    


print(get_genai_advice('user6'))