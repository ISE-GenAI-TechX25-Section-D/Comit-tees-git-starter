import streamlit as sl
from modules import display_my_custom_component, display_post, display_genai_advice
from data_fetcher import get_user_posts, get_user_profile, get_genai_advice

def display_community(user_id):
    user_profile = get_user_profile(user_id)
    sl.title("❤️ Community Page")
    left_col, right_col = sl.columns(2)
    with left_col:
        display_post(user_id)
    with right_col:
        display_genai_advice(user_id)