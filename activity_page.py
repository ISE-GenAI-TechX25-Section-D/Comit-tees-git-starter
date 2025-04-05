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

    data_source = sl.radio("Choose what to share from:", ["My Total Stats", "A Specific Workout"])

    if data_source == "My Total Stats":
        share_total_stats(user_id)
    elif data_source == "A Specific Workout":
        share_specific_workout(user_id, recent_workouts)

def share_total_stats(user_id):

    steps = sl.session_state.get("total_steps", 0)
    distance = sl.session_state.get("total_distance", 0)
    calories = sl.session_state.get("total_calories", 0)

    stat_type = sl.selectbox("Which stat would you like to share?", ["All", "Steps", "Distance", "Calories"])

    if sl.button("📤 Share"):
        if stat_type == "Steps":
            message = f"👟 I walked {steps} steps this week!"
        elif stat_type == "Distance":
            message = f"🏃 I ran {distance} miles this week!"
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
        f"{w['start_timestamp']} | {w['distance']} mi | {w['calories_burned']} cal": w
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





