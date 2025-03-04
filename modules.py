#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from internals import create_component
from data_fetcher import get_user_workouts

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass


def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    """
    Description:
        Displays information about the recent workouts from workouts_list by showing a table of information (and potentially a map, but doesnt look right)
    Input: 
        workouts_list (list):  contains all of the information about the workouts to be displayed
    Output:
        Returns nothing
        Outputs a table to website
    """
    #Made with slight debugging help from Gemini: https://g.co/gemini/share/d246196d413a
    import streamlit as sl
    import pandas as pd
    if 'workouts_list' not in sl.session_state:
        sl.session_state.workouts_list = workouts_list
    sl.title('Recent Workouts') 
    mod_workouts_list = []
    #start_lat_long_list = []
    #end_lat_long_list =[]
    for i in range(len(sl.session_state.workouts_list)):
        mod_workouts_list.append({
            'workout_id': workouts_list[i]['workout_id'],
            'start_timestamp': workouts_list[i]['start_timestamp'],
            'end_timestamp': workouts_list[i]['end_timestamp'],
            'distance': workouts_list[i]['distance'],
            'steps': workouts_list[i]['steps'],
            'calories_burned': workouts_list[i]['calories_burned']
        })
        '''start_lat_long_list.append({
            'start_lat': workouts_list[i]['start_lat_lng'][0],
            'start_long': workouts_list[i]['start_lat_lng'][1]
        })
        end_lat_long_list.append({
            'end_lat': workouts_list[i]['end_lat_lng'][0],
            'end_long': workouts_list[i]['end_lat_lng'][1]
        })'''
        
    df = pd.DataFrame(mod_workouts_list)
    df.columns = ['Workout Name', 'Start Date and Time', 'End Date and Time', 'Total Distance', 'Steps', 'Calories Burned']
    sl.table(df)
    #map is kinda wonky
    '''start_pos = pd.DataFrame(start_lat_long_list)
    end_pos = pd.DataFrame(end_lat_long_list)
    sl.map(start_pos,latitude='start_lat', longitude='start_long')
    sl.map(end_pos,latitude='end_lat', longitude='end_long')'''


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
