#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, Mock, MagicMock
import json
from google.cloud.bigquery import Row
from google.cloud import exceptions as google_exceptions
from google.api_core import exceptions as google_exceptions
from data_fetcher import get_user_workouts, get_user_sensor_data, get_genai_advice
from datetime import datetime
from google.cloud import bigquery

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.vision_models import Image, ImageGenerationModel

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


class TestGetUserSensorData(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_success(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[1])),  # Workout exists and is mapped to user
            Mock(result=Mock(return_value=[
                Mock(SensorId='sensor_a', Timestamp=datetime(2025, 4, 3, 19, 15, 0), SensorValue=120.0),
                Mock(SensorId='sensor_b', Timestamp=datetime(2025, 4, 3, 19, 30, 0), SensorValue=3000.0)
            ])),
            Mock(result=Mock(return_value=[
                Mock(SensorId='sensor_a', Name='Heart Rate', Units='bpm'),
                Mock(SensorId='sensor_b', Name='Step Count', Units='steps')
            ]))
        ]
        MockClient.return_value = mock_client_instance
        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")
        expected_data = [
            {'Timestamp': '2025-04-03 19:15:00', 'Data': 120.0, 'Sensor_type': 'Heart Rate', 'Units': 'bpm'},
            {'Timestamp': '2025-04-03 19:30:00', 'Data': 3000.0, 'Sensor_type': 'Step Count', 'Units': 'steps'},
        ]
        self.assertEqual(actual_data, expected_data)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_invalid_user_id(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [] 

        MockClient.return_value = mock_client_instance

        with self.assertRaises(ValueError) as context:
            get_user_sensor_data(MockClient(), "invalid_user", "test_workout")

        self.assertEqual(str(context.exception), "User ID 'invalid_user' not found.")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_invalid_workout_id(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[])),
        ]
        MockClient.return_value = mock_client_instance

        with self.assertRaises(ValueError) as context:
            get_user_sensor_data(MockClient(), "test_user", "invalid_workout")

        self.assertEqual(str(context.exception), "Workout ID 'invalid_workout' not found or not associated with user ID 'test_user'.")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_success_no_sensor_data(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[1])),  # Workout exists
            Mock(result=Mock(return_value=[])),  # No sensor data
            Mock(result=Mock(return_value=[]))   # No sensor types (still called)
        ]
        MockClient.return_value = mock_client_instance

        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")
        expected_data = []
        self.assertEqual(actual_data, expected_data)
        
    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_missing_sensor_types(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = [
            Mock(result=Mock(return_value=[1])),  # User exists
            Mock(result=Mock(return_value=[1])),
            Mock(result=Mock(return_value=[
                Mock(SensorId='sensor_a', Timestamp=datetime(2025, 4, 3, 19, 15, 0), SensorValue=120.0),
            ])),
            Mock(result=Mock(return_value=[]))
        ]
        MockClient.return_value = mock_client_instance

        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")
        expected_data = [{'Timestamp': '2025-04-03 19:15:00', 'Data': 120.0}]
        self.assertEqual(actual_data, expected_data)

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_bigquery_error(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = google_exceptions.ServiceUnavailable("BigQuery service unavailable")
        MockClient.return_value = mock_client_instance

        with self.assertRaises(google_exceptions.ServiceUnavailable):
            get_user_sensor_data(MockClient(), "test_user", "test_workout")

    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_general_error(self, MockClient):
        mock_client_instance = Mock()
        mock_client_instance.query.side_effect = Exception("General Exception")
        MockClient.return_value = mock_client_instance

        actual_data = get_user_sensor_data(MockClient(), "test_user", "test_workout")

        self.assertEqual(actual_data, [])

class TestGetGenaiAdvice(unittest.TestCase):  
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')
    def test_get_genai_advice_success(self, mock_image_model, mock_text_model, mock_client):
        # Setup BigQuery client mock
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [1]  # User exists
        mock_client.return_value = mock_client_instance
        
        # Setup workouts provider mock
        mock_workouts = [
            {"date": "2025-04-01", "exercise": "Running", "duration": 30},
            {"date": "2025-04-03", "exercise": "Weight training", "duration": 45}
        ]
        mock_workouts_provider = Mock(return_value=mock_workouts)
        
        # Setup text model mock
        mock_text_instance = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({"adviceid": "advice123", "advice": "Mix cardio with strength training for better results."})
        mock_text_instance.generate_content.return_value = mock_response
        mock_text_model.return_value = mock_text_instance
        
        # Setup image model mock
        mock_image_instance = Mock()
        mock_image = Mock()
        mock_image.save = Mock()
        mock_image_response = Mock()
        mock_image_response.images = [mock_image]
        mock_image_instance.generate_images.return_value = mock_image_response
        mock_image_model.return_value = mock_image_instance
        
        # Set fixed timestamp for testing
        test_timestamp = datetime(2025, 4, 5, 12, 0, 0)
        
        # Call the function
        result = get_genai_advice(
            user_id="test_user",
            client=mock_client_instance,
            text_model=mock_text_instance,
            image_model=mock_image_instance,
            workouts_provider=mock_workouts_provider,
            timestamp=test_timestamp
        )
        
        # Assertions
        self.assertEqual(result['advice_id'], "advice123")
        self.assertEqual(result['content'], "Mix cardio with strength training for better results.")
        self.assertTrue(result['image'].startswith("motivation_"))  # Just check the prefix
        self.assertTrue(result['image'].endswith(".png"))  # Just check the suffix
        self.assertEqual(result['timestamp'], "2025-04-05 12:00:00")
        
        # Verify the image was saved with the same filename that's returned
        mock_image.save.assert_called_once_with(result['image'])

    @patch('google.cloud.bigquery.Client')
    def test_get_genai_advice_user_not_found(self, mock_client):
        # Setup BigQuery client mock to return empty result (user not found)
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = []
        mock_client.return_value = mock_client_instance
        
        # Call the function and check for exception
        with self.assertRaises(ValueError) as context:
            get_genai_advice(user_id="nonexistent_user", client=mock_client_instance)
            
        self.assertEqual(str(context.exception), "User ID 'nonexistent_user' not found.")

    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')      
    def test_get_genai_advice_no_workouts(self, mock_image_model, mock_text_model, mock_client):
        # Setup BigQuery client mock
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [1]  # User exists
        mock_client.return_value = mock_client_instance
        
        # Setup workouts provider to return empty list
        mock_workouts_provider = Mock(return_value=[])
        
        # Setup text model mock
        mock_text_instance = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({"adviceid": "advice123", "advice": "Start with light exercises to build a habit."})
        mock_text_instance.generate_content.return_value = mock_response
        mock_text_model.return_value = mock_text_instance
        
        # Setup image model mock
        mock_image_instance = Mock()
        mock_image = Mock()
        mock_image.save = Mock()
        mock_image_response = Mock()
        mock_image_response.images = [mock_image]
        mock_image_instance.generate_images.return_value = mock_image_response
        mock_image_model.return_value = mock_image_instance
        
        # Call the function
        result = get_genai_advice(
            user_id="test_user",
            client=mock_client_instance,
            text_model=mock_text_instance,
            image_model=mock_image_instance,
            workouts_provider=mock_workouts_provider
        )
        
        # Verify the prompt mentions no workouts
        prompt_arg = mock_text_instance.generate_content.call_args[0][0]
        self.assertIn("no recorded workouts", prompt_arg)
        
        # Validate results
        self.assertEqual(result['advice_id'], "advice123")
        self.assertEqual(result['content'], "Start with light exercises to build a habit.")


    @patch('google.cloud.bigquery.Client')
    def test_get_genai_advice_workouts_provider_exception(self, mock_client):
        # Setup BigQuery client mock
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [1]  # User exists
        mock_client.return_value = mock_client_instance
        
        # Setup workouts provider to raise exception
        def workouts_error(user_id):
            raise Exception("Failed to retrieve workouts")
        
        # Call the function
        result = get_genai_advice(
            user_id="test_user",
            client=mock_client_instance,
            workouts_provider=workouts_error
        )
        
        # Verify function gracefully handles the error
        self.assertIsNone(result)
    
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained') 
    def test_get_genai_advice_text_model_exception(self, mock_image_model, mock_text_model, mock_client):
        # Setup BigQuery client mock
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [1]  # User exists
        mock_client.return_value = mock_client_instance
        
        # Setup workouts provider
        mock_workouts = [{"date": "2025-04-01", "exercise": "Running", "duration": 30}]
        mock_workouts_provider = Mock(return_value=mock_workouts)
        
        # Setup text model to raise exception
        mock_text_instance = Mock()
        mock_text_instance.generate_content.side_effect = Exception("Text model failed")
        mock_text_model.return_value = mock_text_instance
        
        # Call the function
        result = get_genai_advice(
            user_id="test_user",
            client=mock_client_instance,
            text_model=mock_text_instance,
            workouts_provider=mock_workouts_provider
        )
        
        # Verify function gracefully handles the error
        self.assertIsNone(result)
    @patch('google.cloud.bigquery.Client')
    @patch('vertexai.generative_models.GenerativeModel')
    @patch('vertexai.vision_models.ImageGenerationModel.from_pretrained')
    def test_get_genai_advice_image_model_exception(self, mock_image_model, mock_text_model, mock_client):
        # Setup BigQuery client mock
        mock_client_instance = Mock()
        mock_client_instance.query.return_value.result.return_value = [1]  # User exists
        mock_client.return_value = mock_client_instance
        
        # Setup workouts provider
        mock_workouts = [{"date": "2025-04-01", "exercise": "Running", "duration": 30}]
        mock_workouts_provider = Mock(return_value=mock_workouts)
        
        # Setup text model mock
        mock_text_instance = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({"adviceid": "advice123", "advice": "Run more consistently"})
        mock_text_instance.generate_content.return_value = mock_response
        mock_text_model.return_value = mock_text_instance
        
        # Setup image model to raise exception
        mock_image_instance = Mock()
        mock_image_instance.generate_images.side_effect = Exception("Image generation failed")
        mock_image_model.return_value = mock_image_instance
        
        # Call the function
        result = get_genai_advice(
            user_id="test_user",
            client=mock_client_instance,
            text_model=mock_text_instance,
            image_model=mock_image_instance,
            workouts_provider=mock_workouts_provider
        )
        
        # Verify advice is still returned but image is None
        self.assertEqual(result['advice_id'], "advice123")
        self.assertEqual(result['content'], "Run more consistently")
        self.assertIsNone(result['image'])

if __name__ == "__main__":
    unittest.main()