#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
import streamlit as sl
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts, users
from data_fetcher import get_user_posts
from unittest.mock import patch, Mock
import pandas as pd


# Write your tests below

#used gemini for assistance
class TestDisplayPost(unittest.TestCase):
    """
    Tests the display_post function:
        valid user + valid friend
        invalid user
        invalid friend
    """
    @patch('streamlit.image')
    @patch('streamlit.subheader')
    @patch('streamlit.write')
    @patch('streamlit.markdown')
    def test_valid_user_posts(self, mock_markdown, mock_write, mock_subheader, mock_image):
        #checks if the info is on the page if user and friends are valid
        display_post('user1')
        self.assertTrue(mock_subheader.call_count > 0)
        self.assertTrue(mock_write.call_count > 0)
        self.assertTrue(mock_image.call_count > 0)
        self.assertTrue(mock_markdown.call_count > 0)

    @patch('streamlit.error')
    def test_invalid_user(self, mock_error):
        #checks for error if invalid user
        display_post('invalid_user')
        mock_error.assert_called_once_with("User not found.")

    @patch('streamlit.warning')
    def test_invalid_friend(self, mock_warning):
        #checks for error if invalid friend
        original_friends = users['user1']['friends']
        users['user1']['friends'] = ['invalid_friend']  # Add invalid friend

        display_post('user1')

        mock_warning.assert_called_once_with("Friend ID 'invalid_friend' not found.")

        users['user1']['friends'] = original_friends #restore friends list.

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function using Streamlit's AppTest."""

    def setUp(self):
        """Set up the AppTest environment using from_function()"""
        
        self.test_workouts = [
            {
                'workout_id': 'workout0',
                "start_timestamp": "2024-03-07 08:00:00",
                "end_timestamp": "2024-03-07 08:30:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 3.2,
                "steps": 4500,
                "calories_burned": 320
            },
            {
                'workout_id': 'workout1',
                "start_timestamp": "2024-03-06 07:30:00",
                "end_timestamp": "2024-03-06 08:00:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 2.5,
                "steps": 3800,
                "calories_burned": 270
            }
        ]

        # Asked LLM help on how to pass kwargs
        self.app = AppTest.from_function(display_activity_summary, kwargs={"workouts_list": self.test_workouts})
        # Line written by ChatGPT

        self.app.run()  # Run the application to apply testing

        self.subheaders = [subh for subh in self.app.subheader]

        # Calculate expected totals
        expected_distance = sum(workout["distance"] for workout in self.test_workouts) # Line written by ChatGPT
        expected_steps = sum(workout["steps"] for workout in self.test_workouts) # Line written by ChatGPT
        expected_calories = sum(workout["calories_burned"] for workout in self.test_workouts) # Line written by ChatGPT

        self.total_distance = expected_distance
        self.total_steps = expected_steps
        self.total_calories = expected_calories

        self.columns = [col for col in self.app.columns]
    
    def test_title_existance(self):
        """Check if title is present"""
        title_elements = [el.value for el in self.app.title]

        # Check for title
        found_title = any("🏋️ Activity Fitness Summary" in text for text in title_elements)
        self.assertTrue(found_title, "Title '🏋️ Activity Fitness Summary' not found!")
    
    def test_app_init_workout_lists(self):
        self.assertEqual(self.app.session_state.workouts_list, self.test_workouts)
    
    def test_select_box(self):
        select_box_elements = [el.label for el in self.app.selectbox]
        # Check for workout selection dropdown
        # Used help of LLM
        found_dropdown = any("Workout (Beta - Only Running has data):" in label for label in select_box_elements)
        self.assertTrue(found_dropdown, "Workout selection dropdown not found!")
    
    def test_workout_type(self):
        self.assertEqual(self.app.session_state.selected_workout, "Running")
    
    def test_calculated_totals(self):

        metrics = [ el.value for el in self.app.metric]

        # In Total values, Total Distance is always the first element
        self.assertEqual(metrics[0], f"{5.7} mi", 
                         f"Total Distance metric incorrect! Expected {self.total_distance} mi")
        
        self.assertEqual(metrics[1], f"{8300}", f"Total Steps isn't correct! Expected {self.total_steps}")
        self.assertEqual(metrics[2], f"{590} cals", f"Total Calories isn't correct! Expected {self.total_calories}")
    
    def test_columns_init(self):

        self.assertEqual(len(self.columns), 3)

    def test_columns_values(self):

        # Checking for first columns where should be displayed Total Distance
        self.assertIn("Total Distance",self.columns[0].metric[0].label, "Label isn't Total Distance!")
        self.assertEqual(f"{self.total_distance} mi", self.columns[0].metric[0].value)

        # Checking for second columns where should be displayed Total Steps
        self.assertIn("Total Steps",self.columns[1].metric[0].label, "Label isn't Total Steps!")
        self.assertEqual(f"{self.total_steps}", self.columns[1].metric[0].value)

         # Checking for first columns where should be displayed Total Calories
        self.assertIn("Total Calories", self.columns[2].metric[0].label, "Label isn't Total Calories!")
        self.assertEqual(f"{self.total_calories} cals", self.columns[2].metric[0].value)
    
    def test_details_table_init(self):

        # Check for first subheader that should appear (first one created)
        self.assertIn("Workout Details", self.subheaders[0].body)

        # Check if size of dataframe is more than 0 (it's not empty)
        self.assertGreater(len(self.app.dataframe), 0)
    
    def test_details_table_values(self):
        # As for the actual function code, utilized LLM
        # to correctly access dataframe data

        import pandas as pd

        # Get the actual dataframe from the Streamlit test response
        df_element = self.app.dataframe  # This is a Streamlit ElementList
        # Line written by ChatGPT
        df = pd.DataFrame(df_element[0].value._data)  # Convert it back to a Pandas DataFrame
        # Line written by ChatGPT

        self.assertIsInstance(df, pd.DataFrame)  # Ensure it's a DataFrame
        # Line written by ChatGPT

        workout_keys = df.columns.tolist()

        for key in workout_keys:
            self.assertIn(key, df.columns)

            expected_lst = []

            for workout in self.test_workouts:
                expected_lst.append(workout[key])
            
            self.assertListEqual(df[key].tolist(),expected_lst)
    
    def test_progress_bar(self):

        # Check for second subheader that should appear (second one created)
        self.assertIn("Weekly Calorie Progress", self.subheaders[1].body)

        self.assertEqual(self.app.session_state.weekly_calorie_goal, 450) # Default calorie goal for now (hardcoded)

        test_progress_bar_amount = min(((self.total_calories / 450) * 100), 100)
        # Line written by ChatGPT

        self.assertEqual(test_progress_bar_amount, self.app.session_state.weekly_calorie_progress_amount)


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def setUp(self):
        """Set up the AppTest environment using from_function()"""
        self.test_workouts = [
            {
                'workout_id': 'workout0',
                "start_timestamp": "2024-03-07 08:00:00",
                "end_timestamp": "2024-03-07 08:30:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 3.2,
                "steps": 4500,
                "calories_burned": 320
            },
            {
                'workout_id': 'workout1',
                "start_timestamp": "2024-03-06 07:30:00",
                "end_timestamp": "2024-03-06 08:00:00",
                'start_lat_lng': (),
                'end_lat_lng': (),
                "distance": 2.5,
                "steps": 3800,
                "calories_burned": 270
            }
        ]
        
        self.app = AppTest.from_function(display_recent_workouts, kwargs={"workouts_list": self.test_workouts})
        self.app.run()

        self.subheaders = [subh for subh in self.app.subheader]
        self.dataframe = self.app.table[0].value #gets the pandas dataframe.
    
    def test_drw_contains_title(self):
        "Checks to make sure the title is present"
        titles = [title.value for title in self.app.title]
        self.assertIn("Recent Workouts", titles, "Title 'Recent Workouts' not found!")

    def test_drw_table_contains_correct_columns(self):
        actual_columns = self.dataframe.columns.tolist() #converts the columns to a list.
        expected_columns = ['Workout Name', 'Start Date and Time', 'End Date and Time', 'Total Distance', 'Steps', 'Calories Burned']
        self.assertEqual(actual_columns, expected_columns, "Table columns do not match expected columns!")

    def test_drw_table_contains_values(self):
        actual_workout_names = self.dataframe["Workout Name"].tolist()
        expected_workout_names = ["workout0", "workout1"]
        self.assertEqual(actual_workout_names, expected_workout_names, "Workout names are not equal!")

        actual_start_date_time = self.dataframe["Start Date and Time"].tolist()
        expected_start_date_time = ["2024-03-07 08:00:00", "2024-03-06 07:30:00"]
        self.assertEqual(actual_start_date_time, expected_start_date_time, "Start Date and Time are not equal!")

        actual_end_date_time = self.dataframe["End Date and Time"].tolist()
        expected_end_date_time = ["2024-03-07 08:30:00", "2024-03-06 08:00:00"]
        self.assertEqual(actual_end_date_time, expected_end_date_time, "End Date and Time are not equal!")

        actual_distance = self.dataframe["Total Distance"].tolist()
        expected_distance = [3.2, 2.5]
        self.assertEqual(actual_distance, expected_distance, "Total Distance are not equal!")

        actual_steps = self.dataframe["Steps"].tolist()
        expected_steps = [4500, 3800]
        self.assertEqual(actual_steps, expected_steps, "Steps are not equal!")

        actual_calories = self.dataframe["Calories Burned"].tolist()
        expected_calories = [320, 270]
        self.assertEqual(actual_calories, expected_calories, "Calories Burned are not equal!")

    def test_drw_data_types(self):
        """Tests that data types in the table are correct."""
        if self.app.table:
            table_element = self.app.table[0]
            df = table_element.value
            self.assertTrue(pd.api.types.is_numeric_dtype(df['Total Distance']), "Total Distance should be numeric.")
            self.assertTrue(pd.api.types.is_numeric_dtype(df['Steps']), "Steps should be numeric.")
            self.assertTrue(pd.api.types.is_numeric_dtype(df['Calories Burned']), "Calories Burned should be numeric.")

    def test_drw_incorrect_data_not_equal(self):
        actual_workout_names = self.dataframe["Workout Name"].tolist()
        incorrect_workout_names = ["workout3", "workout4"]
        self.assertNotEqual(actual_workout_names, incorrect_workout_names, "Workout names are equal!")

        actual_start_date_time = self.dataframe["Start Date and Time"].tolist()
        incorrect_start_date_time = ["2025-03-08 08:00:00", "2024-03-09 07:30:00"]
        self.assertNotEqual(actual_start_date_time, incorrect_start_date_time, "Start Date and Time are equal!")

        actual_end_date_time = self.dataframe["End Date and Time"].tolist()
        incorrect_end_date_time = ["2024-03-08 08:30:00", "2024-03-09 08:00:00"]
        self.assertNotEqual(actual_end_date_time, incorrect_end_date_time, "End Date and Time are equal!")

        actual_distance = self.dataframe["Total Distance"].tolist()
        incorrect_distance = [2.4, 5.7]
        self.assertNotEqual(actual_distance, incorrect_distance, "Total Distance are equal!")

        actual_steps = self.dataframe["Steps"].tolist()
        incorrect_steps = [6000, 1500]
        self.assertNotEqual(actual_steps, incorrect_steps, "Steps are equal!")

        actual_calories = self.dataframe["Calories Burned"].tolist()
        incorrect_calories = [500, 740]
        self.assertNotEqual(actual_calories, incorrect_calories, "Calories Burned are equal!")

    def test_drw_empty_workout_table_contains_subheader(self):
        """Tests that the correct message is displayed for an empty workout list."""
        app = AppTest.from_function(display_recent_workouts, kwargs={"workouts_list": []})
        app.run()
        self.assertIn("No Workout Data To Display", [sub.value for sub in app.subheader], "Empty list message not found!")
        self.assertEqual(app.table, [], "Table should not be displayed for empty list.")


if __name__ == "__main__":
    unittest.main()
