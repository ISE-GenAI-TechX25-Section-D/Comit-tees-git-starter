#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as sl
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts



def display_app_page():
    """Displays the home page of the app."""
    userId = 'user1'
    user_profile = get_user_profile(userId)
    user_name = user_profile['username']

    sl.title(f'Welcome {user_name} to MyFitness!')

    posts, recent_workouts, activity_summary, genai_advice = sl.tabs(["Posts", "Recent Workouts", "Activity Summary", "GenAI Advice"])

    with posts:
        display_post(userId)
    with recent_workouts:
        display_recent_workouts(userId)
    with activity_summary:
        display_activity_summary(fetcher=lambda:get_user_workouts(userId)) # Using dependency injection
    with genai_advice:
        display_genai_advice(get_genai_advice(userId)['timestamp'],get_genai_advice(userId)['content'],get_genai_advice(userId)['image'] )
        
# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
