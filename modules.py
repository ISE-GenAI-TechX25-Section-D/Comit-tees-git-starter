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
from data_fetcher import get_user_workouts, get_user_posts, users, get_genai_advice, get_user_friends, get_user_info, get_user_password,get_user_ID_from_username,create_new_user, username_exists, get_global_calories_list, get_friends_calories_list
from PIL import Image
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, date

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

#used gemini for assistance: 
def display_post(user_id, query_db=bigquery, streamlit_module=sl):
    """
    Displays list of user's friends' posts: includes, pfp, name, username, timestamp, and post.
    """
    friends = get_user_friends(user_id, query_db=query_db)

    streamlit_module.header("Friends' Posts")

    for friend_id in friends:
        friend_info = get_user_info(friend_id, query_db=query_db)
        if friend_info:
            posts = get_user_posts(friend_id, query_db=query_db)

            streamlit_module.image(friend_info['profile_image'], width=100)
            streamlit_module.subheader(f"{friend_info['full_name']} (@{friend_info['username']})")
            for post in posts:
                streamlit_module.write(f"**{post['content']}**")
                streamlit_module.write(f"Posted on: {post['timestamp']}")
                if post['image']:
                    streamlit_module.image(post['image'], width=200)
                streamlit_module.markdown("---")
        else:
            streamlit_module.warning(f"Friend ID '{friend_id}' not found.")

# display_activity_summary(fetcher=lambda: get_user_workouts(user_id)
def display_activity_summary(workouts_list=None, fetcher=None): # fetcher = dependency injection, this set up allows to pass hardcoded data still
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

    if fetcher is not None:
        workouts_list = fetcher()

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
    
    sl.session_state.total_distance = total_distance
    sl.session_state.total_steps = total_steps
    sl.session_state.total_calories = total_calories

    
    # Displaying summary statistics
    col1, col2, col3 = sl.columns(3)
    col1.metric("Total Distance", f"{total_distance} mi")
    col2.metric("Total Steps", f"{total_steps}")
    col3.metric("Total Calories", f"{total_calories} cals")
    
    # Workout Details Table
    sl.subheader("Workout Details")
    df = pd.DataFrame(workouts)
    # Line written by ChatGPT
    df_display = df[["distance", "steps", "calories_burned"]].rename(columns={
    "distance": "Distance (mi)",
    "steps": "Steps Taken",
    "calories_burned": "Calories Burned"
    })

    df_display.index = df_display.index + 1

    sl.dataframe(df_display)
    # Line written by ChatGPT
    
    # Weekly Calorie Progress
    sl.subheader("Weekly Calorie Progress")
    week_goal = 2000  # Default weekly goal
    sl.session_state.weekly_calorie_goal = week_goal
    progress_bar_amount = min(((total_calories / week_goal) * 100), 100)
    # Line written by ChatGPT
    sl.session_state.weekly_calorie_progress_amount = progress_bar_amount
    sl.progress(progress_bar_amount / 100)
    sl.write(f"**Weekly Goal: {week_goal} cal | Current: {total_calories} cal**")


def display_recent_workouts(userId, workouts_func=get_user_workouts, streamlit_module=sl):
    """
    Description:
        Displays information about the recent workouts by the user by showing relevant information about each workout
    Input: 
        userId (string):  the ID of the user whose workouts are being displayed, used as an argument to get_user_workouts
        workouts_func (function): the function to be called to get the user's workout data
        streamlit_module (module): the module to be used to create the website
    Output:
        Returns nothing
        Outputs relevant information to website
    """
    #Made with slight debugging help from Gemini: https://g.co/gemini/share/d246196d413a
    streamlit_module.title('💪Recent Workouts💪')
    workouts_list = workouts_func(userId)
    if len(workouts_list) == 0:
        streamlit_module.subheader("No Workout Data To Display")
        return
    for workout in workouts_list:
        streamlit_module.subheader(workout['workout_id'])
        date = workout['start_timestamp']
        date = date[:date.index(' ')]
        streamlit_module.write(f"📅Date: {date}")
        workout_time = workout['start_timestamp']
        start_time = workout_time[workout_time.index(' ')+1:]
        workout_time = workout['end_timestamp']
        end_time = workout_time[workout_time.index(' ')+1:]
        streamlit_module.write(f"⏱️Time: {start_time} &mdash; {end_time}")
        streamlit_module.write(f"↔️Distance: {workout['distance']} miles")
        streamlit_module.write(f"🚶Steps: {workout['steps']}")
        streamlit_module.write(f"🔥Calories Burned: {workout['calories_burned']} calories")
        streamlit_module.write("---")
    streamlit_module.subheader("Keep up the good work(outs)!")

def display_genai_advice(
    userId,
    advice_func=get_genai_advice,
    streamlit_module=sl
):
    """
    Displays AI-generated fitness advice with a related image.
    
    Args:
        timestamp: When the advice was generated
        content: The advice text content
        image: Path to the generated image
        title: Main title of the section
        subheader: Subheader text
        display_fn: Dependency-injected Streamlit display function
        
    Returns:
        None (renders UI components)
    """
    advice = advice_func(userId)
    timestamp = advice['timestamp']
    content = advice['content']
    image = advice['image']
    title = "AI Fitness Coach🦾"
    subheader = "Personalized advice based on your activities"
    streamlit_module.title(title)
    streamlit_module.subheader(subheader)
    streamlit_module.markdown(content)
    
    if image:  # Only show image if available
        streamlit_module.image(image)
    
    streamlit_module.caption(f"Last updated: {timestamp}")

def login_box():
    sl.subheader("🔐 Login")

    username = sl.text_input("Username")
    password = sl.text_input("Password", type="password")

    login_button = sl.button("Log In")


    if login_button:
        if not username or not password:
            sl.warning("Please enter both username and password.")
            return None

        userID = get_user_ID_from_username(username)
        user_info = get_user_info(userID)
        expected_password = get_user_password(username)

        if user_info is None:
            sl.error("User not found.")
            return False

        if password != expected_password:
            sl.error("Incorrect password.")
            return False

        sl.success(f"Welcome back, {user_info['full_name']}!")
        sl.session_state.userId = userID
        sl.rerun()
        return True  # Can be used to set session state or display more info

    return None

def signup_box():
    sl.subheader("📝 Sign Up")

    # Check for submitted state
    if "signup_submitted" not in sl.session_state:
        sl.session_state.signup_submitted = False

    # If already submitted, show success and login button
    if sl.session_state.signup_submitted:
        sl.success("✅ Account created successfully!")
        if sl.button("Go to Login"):
            sl.session_state.auth_mode = 'login'
            sl.session_state.signup_submitted = False
            sl.rerun()
        return

    first_name = sl.text_input("First Name")
    last_name = sl.text_input("Last Name")
    dob = sl.date_input(
    "Date of Birth",
    value=date(2000, 1, 1),
    min_value=date(1900, 1, 1),
    max_value=datetime.today().date()
    )
    username = sl.text_input("Username")
    image_url = sl.text_input("Profile Image URL (optional)")
    password = sl.text_input("Password", type="password")
    confirm_password = sl.text_input("Confirm Password", type="password")

    signup_button = sl.button("Create Account")

    if signup_button:
        # Validate required fields
        if not all([first_name, last_name, dob, username, password, confirm_password]):
            sl.warning("Please fill in all required fields.")
            return None

        if password != confirm_password:
            sl.error("Passwords do not match.")
            return None

        if username_exists(username):
            sl.error("Username already taken.")
            return None

        full_name = f"{first_name} {last_name}"

        create_new_user(
            username=username,
            name=full_name,
            image_url=image_url,
            date_of_birth=str(dob),
            password=password
            
        )

        sl.success("Account created! You can now log in.")
        sl.session_state.signup_submitted = True
        sl.rerun()

    return None

def display_calories_leaderboard_global(streamlit_module=sl, get_calories_func=get_global_calories_list):
    """
    Displays the global leaderboard of users based on total calories burned,
    with the top 3 on a visual "pedestal".

    Args:
        streamlit_module: The Streamlit module to use for display.
        get_calories_func: The function to fetch the sorted list of (name, calories, user_id).
    """
    leaderboard_data = get_calories_func()

    if leaderboard_data:
        streamlit_module.subheader("🔥 Global Calories Burned Leaderboard 🔥")

        top_3 = leaderboard_data[:3]
        remaining = leaderboard_data[3:5]

        cols = streamlit_module.columns(3)
        pedestal_color = "#D3D3D3"  # Light gray color for the pedestal

        for i, (name, calories, user_id) in enumerate(top_3):
            with cols[i]:
                rank_emoji = ""
                if i == 0:
                    rank_emoji = "🥇"
                elif i == 1:
                    rank_emoji = "🥈"
                elif i == 2:
                    rank_emoji = "🥉"

                streamlit_module.markdown(f"<div style='text-align:center;'>{rank_emoji} <b>{name}</b></div>", unsafe_allow_html=True)
                streamlit_module.markdown(f"<div style='text-align:center;'>{calories} calories</div>", unsafe_allow_html=True)
                streamlit_module.markdown(
                    f"<div style='text-align:center; background-color:{pedestal_color}; padding: 5px; border-radius: 5px;'></div>",
                    unsafe_allow_html=True,
                )

        if remaining:
            streamlit_module.markdown("---")
            streamlit_module.subheader("Top Performers (4th & 5th)")
            for i, (name, calories, user_id) in enumerate(remaining):
                streamlit_module.write(f"**{i + 4}. {name}:** {calories} calories")
    else:
        streamlit_module.info("No calorie data available to display the leaderboard.")

    streamlit_module.markdown("---")
    streamlit_module.subheader("All Participants (Top 10)")
    if leaderboard_data:
        for name, calories, user_id in leaderboard_data[:10]:
            streamlit_module.write(f"**{name}:** {calories} calories burned")
    else:
        streamlit_module.write("No data available.")

# Example of how to use the display_calories_leaderboard function at the bottom of the file
'''
if __name__ == "__main__":
    # This block will only run when this file is executed directly
    # For demonstration purposes, we'll mock the get_global_calories_list function
    def mock_get_global_calories_list():
        return [
            ("Alice", 1500, "user_a"),
            ("Bob", 1250, "user_b"),
            ("Charlie", 1100, "user_c"),
            ("David", 950, "user_d"),
            ("Eve", 800, "user_e"),
            ("Frank", 750, "user_f"),
            ("Grace", 700, "user_g"),
            ("Heidi", 650, "user_h"),
            ("Ivan", 600, "user_i"),
            ("Judy", 550, "user_j"),
        ]

    sl.title("Leaderboard Example")
    display_calories_leaderboard_global(streamlit_module=sl, get_calories_func=mock_get_global_calories_list)
    '''

def display_friends_leaderboard(user_id, streamlit_module=sl, get_friends_calories=get_friends_calories_list):
    """
    Displays the leaderboard of the user and their friends based on total calories burned,
    with the top 3 on a visual "pedestal".

    Args:
        user_id: The ID of the current user.
        streamlit_module: The Streamlit module to use for display.
        get_friends_calories: The function to fetch the sorted list of (name, calories, user_id) for the user and their friends.
    """
    friends_leaderboard_data = get_friends_calories(user_id)

    if friends_leaderboard_data:
        streamlit_module.subheader("👯 Friends' Calories Burned Leaderboard 👯")

        top_3 = friends_leaderboard_data[:3]
        remaining = friends_leaderboard_data[3:5]
        pedestal_color = "#ADD8E6"  # Light blue color for the friends' pedestal

        cols = streamlit_module.columns(3)

        for i, (name, calories, friend_user_id) in enumerate(top_3):
            with cols[i]:
                rank_emoji = ""
                if i == 0:
                    rank_emoji = "🥇"
                elif i == 1:
                    rank_emoji = "🥈"
                elif i == 2:
                    rank_emoji = "🥉"

                streamlit_module.markdown(f"<div style='text-align:center;'>{rank_emoji} <b>{name}</b></div>", unsafe_allow_html=True)
                streamlit_module.markdown(f"<div style='text-align:center;'>{calories} calories</div>", unsafe_allow_html=True)
                streamlit_module.markdown(
                    f"<div style='text-align:center; background-color:{pedestal_color}; padding: 5px; border-radius: 5px; height: 10px;'></div>",
                    unsafe_allow_html=True,
                )

        if remaining:
            streamlit_module.markdown("---")
            streamlit_module.subheader("Top Friends (4th & 5th)")
            for i, (name, calories, friend_user_id) in enumerate(remaining):
                streamlit_module.write(f"**{i + 4}. {name}:** {calories} calories")
    else:
        streamlit_module.info("No calorie data available for you or your friends to display the leaderboard.")

    streamlit_module.markdown("---")
    streamlit_module.subheader("Friends' Performance (Top 10)")
    if friends_leaderboard_data:
        for name, calories, friend_user_id in friends_leaderboard_data[:10]:
            streamlit_module.write(f"**{name}:** {calories} calories burned")
    else:
        streamlit_module.write("No data available for your friends.")


# Example of how to use the display_friends_leaderboard function at the bottom of the file
'''
if __name__ == "__main__":
    # This block will only run when this file is executed directly
    # For demonstration purposes, we'll mock the get_friends_calories_list function
    def mock_get_friends_calories_list(user_id):
        if user_id == "test_user":
            return [
                ("Test User", 1300, "test_user"),
                ("Friend A", 1150, "friend_a"),
                ("Friend B", 1000, "friend_b"),
                ("Friend C", 900, "friend_c"),
                ("Friend D", 780, "friend_d"),
                ("Friend E", 700, "friend_e"),
                ("Friend F", 650, "friend_f"),
            ]
        else:
            return []

    sl.title("Friends Leaderboard Example")
    test_user_id = "test_user"
    display_friends_leaderboard(user_id=test_user_id, streamlit_module=sl, get_friends_calories=mock_get_friends_calories_list)
    '''