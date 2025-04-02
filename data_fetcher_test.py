#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, Mock
from data_fetcher import get_user_workouts
from datetime import datetime

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

        

if __name__ == "__main__":
    unittest.main()