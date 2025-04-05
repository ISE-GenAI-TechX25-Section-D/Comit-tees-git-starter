import streamlit as sl
from data_fetcher import get_user_workouts, insert_user_post
from modules import display_activity_summary, display_recent_workouts

def display(user_id="user1"):
    sl.title("🏃‍♂️ Activities Dashboard")

    fetcher = lambda: get_user_workouts(user_id)
    workouts = fetcher() 
    recent_workouts = workouts[-3:] if len(workouts) >= 3 else workouts

    side_view(user_id, fetcher)
    
    total_distance = sl.session_state.get("total_distance", 0)
    total_steps = sl.session_state.get("total_steps", 0)
    total_calories = sl.session_state.get("total_calories", 0)

    handle_share_section(user_id, workouts, recent_workouts)

def side_view(user_id, fetcher):
    left_col, right_col = sl.columns(2)

    with left_col:
        sl.subheader("🕒 Recent Workouts")
        # display_activity_summary expects a fetcher function
        display_recent_workouts(userId=user_id, workouts_func=get_user_workouts, streamlit_module=sl)

    with right_col:
        sl.subheader("📊 Summary")
        # display_recent_workouts directly takes the get_user_workouts function
        display_activity_summary(fetcher=fetcher)


def handle_share_section(user_id, workouts, recent_workouts):

    sl.markdown("---")
    sl.subheader("📣 Share with the Community")

    share_mode = sl.radio("What would you like to share?", ["My Total Stats", "A Specific Workout"])

    if share_mode == "My Total Stats":
        share_total_stats(user_id)
    elif share_mode == "A Specific Workout":
        share_specific_workout(user_id, recent_workouts)

def share_total_stats(user_id):

    total_steps = sl.session_state.get("total_steps", 0)
    total_distance = sl.session_state.get("total_distance", 0)
    total_calories = sl.session_state.get("total_calories", 0)

    if sl.button("📤 Share Total Stats"):
        message = (
            f"🔥 This week I walked {total_steps} steps, "
            f"ran {total_distance} miles, and burned {total_calories} calories!"
        )
        insert_user_post(user_id, message)
        sl.success("✅ Total stats shared!")

def share_specific_workout(user_id, recent_workouts):
    from data_fetcher import insert_user_post

    if not recent_workouts:
        sl.info("No workouts available to share.")
        return

    # Format dropdown options
    workout_options = {
        f"{w['start_timestamp']} | {w['distance']} mi | {w['calories_burned']} cal": w
        for w in reversed(recent_workouts)
    }

    selected_label = sl.selectbox("Choose a workout to share:", list(workout_options.keys()))
    selected_workout = workout_options[selected_label]

    if sl.button("📤 Share This Workout"):
        date = selected_workout['start_timestamp'].split(' ')[0]
        message = (
            f"🏃 On {date}, I completed a {selected_workout['distance']} mile run, "
            f"took {selected_workout['steps']} steps, and burned {selected_workout['calories_burned']} calories!"
        )
        insert_user_post(user_id, message)
        sl.success("✅ Workout shared!")




