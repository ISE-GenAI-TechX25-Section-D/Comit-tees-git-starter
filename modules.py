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
from data_fetcher import get_user_workouts, get_user_posts, users
from PIL import Image
import pandas as pd


#add your tab to the list when you're ready, https://docs.streamlit.io/develop/api-reference/layout/st.tabs
recent_workouts_tab, post_tab, gen_ai_advice_tab = sl.tabs(['Recent Workouts', 'Posts', 'Gen AI Advice'])
 
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


#used gemini for assistance
def display_post(user_id):
    """
    Description:
        Displays list of user's friends' posts: includes, pfp, name, username, timestamp, and post
    Input:
        User(id): whoever is logged in
    Output:
        None: instead, shows the user's friends' posts as well as info on the page
    """

    if user_id not in users:
        sl.error("User not found.")
        return

    user = users[user_id]
    friends = user['friends']

    sl.header("Friends' Posts")

    for friend_id in friends:
        if friend_id in users:
            
            friend = users[friend_id]
            posts = get_user_posts(friend_id)

            sl.image(friend['profile_image'], width=100)
            sl.subheader(f"{friend['full_name']} (@{friend['username']})")
            for post in posts:
                sl.write(f"**{post['content']}**")
                sl.write(f"Posted on: {post['timestamp']}")
                if post['image']:
                    sl.image(post['image'], width=200)
                sl.markdown("---")  # Separator between posts
        else:
            sl.warning(f"Friend ID '{friend_id}' not found.")

'''
def main():
    sl.title("Social Media Feed")

    user_id = sl.selectbox("Select a User", list(users.keys()))

    if sl.button("Show Feed"):
        display_post(user_id)

if __name__ == "__main__":
    main()
'''


def display_activity_summary(workouts_list):
    import streamlit as sl
    import pandas as pd
    
    """
    Description: 
        Displays an activity summary for the user's workouts.
        This function presents an overview of the user's fitness activity by:
            - Allowing the user to select a workout type (currently limited to "Running").
            - Displaying total distance, total steps, and total calories burned.
            - Showing a detailed table of past workouts, including timestamps, distance, steps, and calories burned.
            - Visualizing weekly calorie progress with a progress bar.
    Input:
        workouts_list (list of dict): A list of workout dictionaries, where each workout contains:
            - 'workout_id' (str): A unique identifier for the workout.
            - 'start_timestamp' (str): The start time of the workout.
            - 'end_timestamp' (str): The end time of the workout.
            - 'start_lat_lng' (tuple): Starting latitude and longitude.
            - 'end_lat_lng' (tuple): Ending latitude and longitude.
            - 'distance' (float): Distance covered in miles.
            - 'steps' (int): Number of steps taken.
            - 'calories_burned' (int): Calories burned during the workout.
    Output:
        None
    """

    sl.title("🏋️ Activity Fitness Summary")
    
    # workout_options = ["Running", "Full Body", "Chest", "Cardio", "Back"] # Using list when workout types are available

    workout_options = ["Running"]

    if 'workouts_list' not in sl.session_state:
            sl.session_state.workouts_list = workouts_list
    
    if "selected_workout" not in sl.session_state:
        sl.session_state.selected_workout = workout_options[0]
    
    workout_type = sl.selectbox("Workout (Beta - Only Running has data):", workout_options, key="workout_selector")
    
    # Refresh workouts only when selection changes
    if workout_type != sl.session_state.selected_workout:
        sl.session_state.selected_workout = workout_type
    
    workouts = sl.session_state.workouts_list

    # Summary metrics
  
    total_distance = 0
    total_steps = 0
    total_calories = 0

    for workout in workouts:
        total_distance += workout['distance']
        total_steps += workout['steps']
        total_calories += workout['calories_burned']

    
    # Displaying summary statistics
    col1, col2, col3 = sl.columns(3)
    col1.metric("Total Distance", f"{total_distance} mi")
    col2.metric("Total Steps", f"{total_steps}")
    col3.metric("Total Calories", f"{total_calories} cals")
    
    # Workout Details Table
    sl.subheader("Workout Details")
    df = pd.DataFrame(workouts)
    sl.dataframe(df[["start_timestamp", "end_timestamp", "distance", "steps", "calories_burned"]])
    
    # Weekly Calorie Progress
    sl.subheader("Weekly Calorie Progress")
    week_goal = 450  # Default weekly goal
    sl.session_state.weekly_calorie_goal = week_goal
    progress_bar_amount = min(((total_calories / week_goal) * 100), 1.0)
    sl.session_state.weekly_calorie_progress_amount = progress_bar_amount
    sl.progress(progress_bar_amount / 100)
    sl.write(f"**Weekly Goal: {week_goal} cal | Current: {total_calories} cal**")


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
        sl.title('Recent Workouts') 
        if len(workouts_list) == 0:
            sl.subheader("No Workout Data To Display")
            return
        elif 'workouts_list' not in sl.session_state:
            sl.session_state.workouts_list = workouts_list
        mod_workouts_list = []
        for i in range(len(sl.session_state.workouts_list)):
            mod_workouts_list.append({
                'workout_id': workouts_list[i]['workout_id'],
                'start_timestamp': workouts_list[i]['start_timestamp'],
                'end_timestamp': workouts_list[i]['end_timestamp'],
                'distance': workouts_list[i]['distance'],
                'steps': workouts_list[i]['steps'],
                'calories_burned': workouts_list[i]['calories_burned']
            })
            
        df = pd.DataFrame(mod_workouts_list)
        df.columns = ['Workout Name', 'Start Date and Time', 'End Date and Time', 'Total Distance', 'Steps', 'Calories Burned']
        sl.table(df)


def display_genai_advice(timestamp, content, image):
    import streamlit as sl
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
