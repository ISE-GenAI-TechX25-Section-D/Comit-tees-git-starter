import streamlit as sl
from modules import display_my_custom_component, display_post
from data_fetcher import get_user_posts, get_user_profile

def display_community(user_id):
    user_profile = get_user_profile(user_id)
    sl.title("❤️ Community Page")
    sl.subheader(f" {user_profile['full_name']}'s")
    display_post(user_id)