#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, Mock, call, MagicMock
from data_fetcher import get_user_workouts, get_user_posts, get_user_friends, get_user_info, get_user_profile
from datetime import datetime
from google.cloud import bigquery


class TestDataFetcher(unittest.TestCase):

    def test_foo(self):
        """Tests foo."""
        pass
    
    def mock_execute_query(self, client, query):
        return [
            ('workout1', 'user1', datetime(2024, 7, 29, 7, 0, 0), datetime(2024, 7, 29, 8, 0, 0), 37.7749, -122.4194, 37.8049, -122.421, 5.0, 8000, 400.0),
            ('workout2', 'user1', datetime(2024, 7, 30, 7, 0, 0), datetime(2024, 7, 30, 8, 0, 0), 38.7749, -123.4194, 38.8049, -123.421, 6.0, 9000, 500.0),
        ]
    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_queries_db(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_query_job.result.return_value = self.mock_execute_query(mock_client, mock_query_job)
        mock_client.query.return_value = mock_query_job
        workouts = get_user_workouts('user1')
        self.assertTrue(mock_big_query_client.call_count > 0, 'Database not called!')
    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_first_list_correct(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_query_job.result.return_value = self.mock_execute_query(mock_client, mock_query_job)
        mock_client.query.return_value = mock_query_job
        workouts = get_user_workouts('user1')
        self.assertTrue(workouts[0]['workout_id'], 'workout1')
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 29, 7, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 29, 8, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_lat_lng'], (37.7749, -122.4194))
        self.assertTrue(workouts[0]['end_lat_lng'], (37.8049, -122.421))
        self.assertTrue(workouts[0]['distance'], 5.0)
        self.assertTrue(workouts[0]['steps'], 8000)
        self.assertTrue(workouts[0]['calories_burned'], 400.0)
    @patch('google.cloud.bigquery.Client')
    def test_get_user_workouts_second_list_correct(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_query_job.result.return_value = self.mock_execute_query(mock_client, mock_query_job)
        mock_client.query.return_value = mock_query_job
        workouts = get_user_workouts('user1')
        self.assertTrue(workouts[0]['workout_id'], 'workout2')
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 30, 7, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_timestamp'], datetime(2024, 7, 30, 8, 0, 0).strftime('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(workouts[0]['start_lat_lng'], (38.7749, -123.4194))
        self.assertTrue(workouts[0]['end_lat_lng'], (38.8049, -123.421))
        self.assertTrue(workouts[0]['distance'], 6.0)
        self.assertTrue(workouts[0]['steps'], 9000)
        self.assertTrue(workouts[0]['calories_burned'], 500.0)

#used gemini for assistance:        
class TestGetUserFriends(unittest.TestCase):

    def mock_execute_query_friends(self, client, query):
        if "Friends" in query:
            return [("friend1",), ("friend2",), ("friend3",)]
        else:
            return []  # Return empty if it's not the Friends query

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_basic(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job  # Mock the query call

        # Call get_user_friends with the custom execute_query function
        friends = get_user_friends(
            "user1",
            execute_query=self.mock_execute_query_friends
        )

        expected_friends = ["friend1", "friend2", "friend3"]

        self.assertEqual(friends, expected_friends)

    def mock_execute_query_no_friends(self, client, query):
        return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_no_friends(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        friends = get_user_friends(
            "user2",
            execute_query=self.mock_execute_query_no_friends
        )

        expected_friends = []

        self.assertEqual(friends, expected_friends)

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

#used gemini for assistance: 
class TestGetUserPosts(unittest.TestCase):

    def mock_execute_query_posts(self, client, query):
        if "Posts" in query:
            return [
                ("post1", "user1", datetime(2023, 11, 15, 12, 30, 0), "image1.jpg", "Hello world!"),
                ("post2", "user1", datetime(2023, 11, 16, 14, 45, 0), "image2.jpg", "Another post."),
            ]
        else:
            return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_posts_basic(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        posts = get_user_posts("user1", execute_query=self.mock_execute_query_posts)

        expected_posts = [
            {
                "post_id": "post1",
                "user_id": "user1",
                "timestamp": "2023-11-15 12:30:00",
                "image": "image1.jpg",
                "content": "Hello world!",
            },
            {
                "post_id": "post2",
                "user_id": "user1",
                "timestamp": "2023-11-16 14:45:00",
                "image": "image2.jpg",
                "content": "Another post.",
            },
        ]

        self.assertEqual(posts, expected_posts)

    def mock_execute_query_no_posts(self, client, query):
        return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_posts_no_posts(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        posts = get_user_posts("user2", execute_query=self.mock_execute_query_no_posts)

        expected_posts = []

        self.assertEqual(posts, expected_posts)

#used gemini for assistance: 
class TestGetUserFriends(unittest.TestCase):

    def mock_execute_query_friends(self, client, query):
        if "Friends" in query:
            return [("friend1",), ("friend2",), ("friend3",)]
        else:
            return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_basic(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        friends = get_user_friends("user1", execute_query=self.mock_execute_query_friends)

        expected_friends = ["friend1", "friend2", "friend3"]

        self.assertEqual(friends, expected_friends)

    def mock_execute_query_no_friends(self, client, query):
        return []

    @patch('google.cloud.bigquery.Client')
    def test_get_user_friends_no_friends(self, mock_big_query_client):
        mock_client = Mock()
        mock_big_query_client.return_value = mock_client
        mock_query_job = Mock()
        mock_client.query.return_value = mock_query_job

        friends = get_user_friends("user2", execute_query=self.mock_execute_query_no_friends)

        expected_friends = []

        self.assertEqual(friends, expected_friends)

class TestGetUserProfile(unittest.TestCase):

    def make_mock_result(self, rows):
        mock_result = MagicMock()
        mock_result.total_rows = len(rows)
        mock_result.__iter__.return_value = iter(rows)  # Makes it iterable like BigQuery results
        return mock_result


    def mock_execute_query_profile(self, client, query):
        if "Users" in query:
            rows = [(
                "Remi",                     # Name
                "remi_the_rems",            # Username
                "https://img.jpg",          # ImageUrl
                datetime(1990, 1, 1)        # DateOfBirth
            )]
            return self.make_mock_result(rows)
        return self.make_mock_result([])


    def mock_execute_query_friends(self, client, query):
        rows = []
        if "Friends" in query:
            rows = [("user2",), ("user3",)]

        mock_result = MagicMock()
        mock_result.total_rows = len(rows)
        mock_result.__iter__.return_value = iter(rows)

        return mock_result


    @patch('google.cloud.bigquery.Client')
    def test_get_user_profile_returns_correct_data(self, mock_big_query_client):
        mock_client = MagicMock()
        mock_big_query_client.return_value = mock_client

        with patch('data_fetcher.get_user_friends', return_value=["user2", "user3"]):
            user_profile = get_user_profile(
                "user1", 
                execute_query=self.mock_execute_query_profile
            )

        expected = {
            "full_name": "Remi",
            "username": "remi_the_rems",
            "profile_image": "https://img.jpg",
            "date_of_birth": "1990-01-01",
            "friends": ["user2", "user3"]
        }

        self.assertEqual(user_profile, expected)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_profile_raises_error_on_user_not_found(self, mock_big_query_client):
        mock_client = MagicMock()
        mock_big_query_client.return_value = mock_client

        with self.assertRaises(ValueError):
            get_user_profile("userX", execute_query=self.mock_execute_query_user_not_found)
    
    def mock_execute_query_user_not_found(self, client, query):
        return self.make_mock_result([])



if __name__ == "__main__":
    unittest.main()