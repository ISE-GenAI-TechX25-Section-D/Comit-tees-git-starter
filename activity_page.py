import streamlit as sl
from data_fetcher import get_user_workouts, insert_user_post
from modules import display_activity_summary, display_recent_workouts
from datetime import datetime

#Used GPT 4o to help with share logic

def display_activity_page(user_id="user1"):
    # sl.title("🏃‍♂️ Activities Dashboard")

    fetcher = lambda: get_user_workouts(user_id)
    workouts = fetcher() 

    # Sort by timestamp descending (most recent first)
    sorted_workouts = sorted(
        workouts,
        key=lambda w: w['start_timestamp'][:w['start_timestamp'].index(' ')],
        reverse=True
    )

    # Get the 3 most recent
    recent_workouts = sorted_workouts[:3]

    side_view(user_id, recent_workouts)

    total_distance = sl.session_state.get("total_distance", 0)
    total_steps = sl.session_state.get("total_steps", 0)
    total_calories = sl.session_state.get("total_calories", 0)

    handle_share_section(user_id, workouts, recent_workouts)

def side_view(user_id, workouts_list):
    left_col, right_col = sl.columns(2)

    with left_col:
        # Developeed with GPT 4o
        display_recent_workouts(
            user_id,
            workouts_func=lambda uid: sorted(get_user_workouts(uid), key=lambda w: w['start_timestamp'], reverse=True)[:3]
        )

    with right_col:
        display_activity_summary(workouts_list)


def handle_share_section(user_id, workouts, recent_workouts):
    sl.markdown("---")
    sl.subheader("📣 Share with the Community")

    data_source = sl.radio("Choose what to share from:", ["My Total Stats", "A Specific Workout"])

    if data_source == "My Total Stats":
        share_total_stats(user_id)
    elif data_source == "A Specific Workout":
        share_specific_workout(user_id, recent_workouts)
    sl.markdown("---")
    sl.markdown("When you press the sharing button, wait a few seconds until the shared notification appears!")
    

def share_total_stats(user_id):

    steps = sl.session_state.get("total_steps", 0)
    distance = sl.session_state.get("total_distance", 0)
    calories = sl.session_state.get("total_calories", 0)

    stat_type = sl.selectbox("Which stat would you like to share?", ["All", "Steps", "Distance", "Calories"])

    if sl.button("📤 Share"):
        if stat_type == "Steps":
            message = f"👟 I walked {round(steps)} steps this week!"
        elif stat_type == "Distance":
            message = f"🏃 I ran {round(distance)} miles this week!"
        elif stat_type == "Calories":
            message = f"🔥 I burned {calories} calories this week!"
        elif stat_type == "All":
            message = (
                f"📊 This week I walked {steps} steps, "
                f"ran {distance} miles, and burned {calories} calories!"
            )

        insert_user_post(user_id, message)
        sl.success("✅ Shared!")


def share_specific_workout(user_id,recent_workouts):
    
    if not recent_workouts:
        sl.info("No recent workouts to share.")
        return

    workout_options = {
        f"{ w['workout_id']} - ( { w['start_timestamp']} | {w['distance']} mi | {w['calories_burned']} cal )": w
        for w in reversed(recent_workouts)
    }
    selected_label = sl.selectbox("Choose a workout:", list(workout_options.keys()))
    selected_workout = workout_options[selected_label]
    date = selected_workout['start_timestamp'].split(' ')[0]

    stat_type = sl.selectbox("Which stat would you like to share?", ["All", "Steps", "Distance", "Calories"])

    if sl.button("📤 Share"):
        if stat_type == "Steps":
            message = f"👟 On {date}, I walked {selected_workout['steps']} steps!"
        elif stat_type == "Distance":
            message = f"🏃 On {date}, I ran {selected_workout['distance']} miles!"
        elif stat_type == "Calories":
            message = f"🔥 On {date}, I burned {selected_workout['calories_burned']} calories!"
        elif stat_type == "All":
            message = (
                f"🏋️ On {date}, I ran {selected_workout['distance']} miles, "
                f"took {selected_workout['steps']} steps, and burned {selected_workout['calories_burned']} calories!"
            )

        insert_user_post(user_id, message)
        sl.success("✅ Shared!")





