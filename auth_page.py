import streamlit as sl
from data_fetcher import get_user_workouts, insert_user_post,get_user_sensor_data
from modules import login_box
from datetime import datetime
import pandas as pd
from google.cloud import bigquery

def display_login():
    login_box()

def logout():
    sl.session_state.clear()
    sl.query_params.clear()
    sl.rerun()
