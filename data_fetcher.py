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


def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestampped information for a given workout.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    sensor_data = []
    sensor_types = [
        'accelerometer',
        'gyroscope',
        'pressure',
        'temperature',
        'heart_rate',
    ]
    for index in range(random.randint(5, 100)):
        random_minute = str(random.randint(0, 59))
        if len(random_minute) == 1:
            random_minute = '0' + random_minute
        timestamp = '2024-01-01 00:' + random_minute + ':00'
        data = random.random() * 100
        sensor_type = random.choice(sensor_types)
        sensor_data.append(
            {'sensor_type': sensor_type, 'timestamp': timestamp, 'data': data}
        )
    return sensor_data


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
