import streamlit as sl
from data_fetcher import get_user_workouts
from modules import display_activity_summary, display_recent_workouts

def display(user_id="user1"):
    st.title("🏃‍♂️ Activities Dashboard")

    # Layout: side-by-side view
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("📊 Summary")
        # display_activity_summary expects a fetcher function
        display_activity_summary(fetcher=lambda: get_user_workouts(user_id))

    with right_col:
        st.subheader("🕒 Recent Workouts")
        # display_recent_workouts directly takes the get_user_workouts function
        display_recent_workouts(userId=user_id, workouts_func=get_user_workouts, streamlit_module=st)
