#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import streamlit as sl
from internals import create_component
from data_fetcher import get_user_workouts
from data_fetcher import get_user_posts
from PIL import Image

#add your tab to the list when you're ready, https://docs.streamlit.io/develop/api-reference/layout/st.tabs
recent_workouts_tab = sl.tabs(['Recent Workouts'])

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
    """
    Description:
        Displays post content and username/pfp on the page
    Input:
        Username, pfp image, date/time, image content, text posted
    Output:
        None, instead, shows the user's posts as well as info on the page
    """
    
    user = sl.text_input('Search Posts')
    user = username
    pic_col, post_col = sl.columns([1, 1])
    
    with post_col: 
        pfp_col, text_col = sl.columns([1, 2])
        with pfp_col:
            sl.image(user_image, width = 100)
            
        with text_col:
            sl.write(user)
        sl.write(timestamp)
        sl.write("---") 
        sl.write(content)
                
    with pic_col:
        sl.image(post_image, width = 300)

#if __name__ == '__main__':
#display_post('Remi', 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg', '2024-01-01 00:00:00', 'Had a great workout today!', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSz0kSuHwimKiIaNdUXwlaLMlkmnTXVC36Qkg&s')
    

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
    import pandas as pd
    with recent_workouts_tab:
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
            # start_lat_long_list.append({
            #     'start_lat': workouts_list[i]['start_lat_lng'][0],
            #     'start_long': workouts_list[i]['start_lat_lng'][1]
            # })
            # end_lat_long_list.append({
            #     'end_lat': workouts_list[i]['end_lat_lng'][0],
            #     'end_long': workouts_list[i]['end_lat_lng'][1]
            # })
            
        df = pd.DataFrame(mod_workouts_list)
        df.columns = ['Workout Name', 'Start Date and Time', 'End Date and Time', 'Total Distance', 'Steps', 'Calories Burned']
        sl.table(df)
        #map is kinda wonky
        # start_pos = pd.DataFrame(start_lat_long_list)
        # end_pos = pd.DataFrame(end_lat_long_list)
        # sl.map(start_pos,latitude='start_lat', longitude='start_long')
        # sl.map(end_pos,latitude='end_lat', longitude='end_long')


def display_genai_advice(timestamp, content, image):
    """
    Description: Displays advice developed by the AI model along with a related image.
    Input: A timestamp, content, and image.
    Output: Returns Nothing
            Outputs a page containing the advice and image.
    """
    sl.title("AI Fitness Coach")
    sl.subheader("Personalized advice based on your activities")
    sl.markdown(content)
    sl.image(image)
    sl.markdown(f"Last updated: {timestamp}")
